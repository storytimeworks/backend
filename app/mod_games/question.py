from app import db
from app.chinese import segment
from app.mod_mastery import Mastery
from app.mod_vocab import Entry

from flask_login import current_user
import json, math, numpy as np

class Question(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    @classmethod
    def play_game(cls, words=None):
        # The number of questions to return
        NUM_QUESTIONS = cls.num_questions if hasattr(cls, "num_questions") else 10

        # The greatest number of questions to show the user that they have
        # previously answered incorrectly
        MAX_WRONG_QUESTIONS = 3

        # The greatest number of questions to show the user that they have
        # previously answered correctly
        MAX_CORRECT_QUESTIONS = 2

        # If the user has answered fewer than MAX_WRONG_QUESTIONS questions
        # incorrectly, this value may be used in place of MAX_CORRECT_QUESTIONS
        MAX_CORRECT_QUESTIONS_WITH_FEW_WRONG_QUESTIONS = 3

        # Mean of the normal distribution used to find question difficulties
        DIFFICULTY_RNORM_MEAN = 17.5

        # Standard deviation of the normal distribution used to find question
        # difficulties
        DIFFICULTY_RNORM_STDEV = 5

        # The list of ids of the questions that should be included in the final result
        question_ids_to_show = []

        # Order by timestamp ascending in order to calculate streaks correctly
        results = cls.result_type.query.filter_by(user_id=current_user.id) \
                    .order_by(cls.result_type.timestamp.asc()).all()

        # Set of the question ids that the user has already seen
        seen_question_ids = set()

        # Maps question ids to the number of games ago where they were last seen
        question_games_ago = {}

        # Maps question ids to the number of times they've been answered correctly
        # in a row. If last answered incorrectly, this equals -1. If never seen
        # before, the question id will not be in this dictionary
        question_streaks = {}

        # Loop through past Scribe results
        for (idx, result) in enumerate(results):
            # Loop through questions answered correctly to calculate streaks
            for id in json.loads(result.correct_question_ids):
                if id in question_streaks:
                    question_streaks[id] += 1
                else:
                    question_streaks[id] = 1

                # Games ago = number of games played - current index in loop
                question_games_ago[id] = len(results) - idx

                # Add this id to the seen_question_ids set
                seen_question_ids.add(id)

            # Loop through questions answered incorrectly to reset streaks
            for id in json.loads(result.wrong_question_ids):
                question_streaks[id] = -1

                # Games ago = number of games played - current index in loop
                question_games_ago[id] = len(results) - idx

                # Add this id to the seen_question_ids set
                seen_question_ids.add(id)

        # Get all of the questions that were last answered incorrectly
        wrong_questions = [x for x in question_streaks if question_streaks[x] == -1]

        if len(wrong_questions) > 0:
            # Make sure our sample size is not greater than the list's length
            num_wrong_questions_to_show = min(len(wrong_questions), MAX_WRONG_QUESTIONS)

            # Randomly sample the wrong_questions list
            wrong_questions_to_show = np.random.choice(wrong_questions, num_wrong_questions_to_show, False)

            # Add these question ids to the result list
            question_ids_to_show.extend(wrong_questions_to_show)

        # Get all of the questions that were last answered correctly, but make sure
        # they weren't answered too recently. games_ago must be >= (streak)^2
        correct_questions = [x for x in question_streaks if question_streaks[x] >= 0 and question_games_ago[x] >= question_streaks[x] ** 2]

        if len(correct_questions) > 0:
            # Make sure our sample size is not greater than the list's length
            num_correct_questions_to_show = min(len(correct_questions), MAX_CORRECT_QUESTIONS if len(wrong_questions) < MAX_WRONG_QUESTIONS else MAX_CORRECT_QUESTIONS_WITH_FEW_WRONG_QUESTIONS)

            # Randomly sample the correct questions list
            correct_questions_to_show = np.random.choice(correct_questions, num_correct_questions_to_show, False)

            # Add these question ids to the result list
            question_ids_to_show.extend(correct_questions_to_show)

        # Make sure questions that have been seen before but were not selected are
        # not in the pool of questions that may be picked at random. Include
        # questions that will be shown to the user so we can get their data
        excluded_question_ids = list(seen_question_ids)
        excluded_question_ids = [id for id in excluded_question_ids if id not in question_ids_to_show]

        questions = []

        if words == None or len(words) == 0:
            # Retrieve all Scribe questions that have not been seen before by the user
            questions = cls.query.filter(cls.id.notin_(excluded_question_ids)).all()
        else:
            # Create a filter that checks for the words provided
            word_filter = cls.chinese.contains(words[0])

            for word in words[1:]:
                word_filter = word_filter | cls.chinese.contains(word)

            # Retrieve all Scribe questions that match both filters
            questions = cls.query.filter(
                cls.id.notin_(excluded_question_ids) & word_filter
            ).all()

        questions_data = [question.serialize() for question in questions]

        # After getting data of questions to show, remove them from questions_data
        # so they will not be randomly picked again later
        questions_to_show = [datum for datum in questions_data if datum["id"] in question_ids_to_show]
        questions_data = [datum for datum in questions_data if datum["id"] not in question_ids_to_show]

        # A list of all of the words seen in every Scribe question
        words = set()

        for question in questions_data:
            # Add this question's words to the words set
            words.update(question["words"])

        # Only retrieve the entries that we need
        entries = Entry.query.filter(Entry.chinese.in_(words)).all()
        entry_ids = [entry.id for entry in entries]

        # Only retrieve the masteries that we need
        masteries = Mastery.query.filter(
            (Mastery.user_id == current_user.id) &
            Mastery.entry_id.in_(entry_ids)
        ).all()

        # Maps Chinese words to their difficulty scores
        difficulties = {}

        # Calculate the difficulty score of each word, using the lists of entries
        # and the user's masteries with them
        for entry in entries:
            mastery = next((x for x in masteries if x.entry_id == entry.id), None)

            if mastery is None:
                # An entry exists for this word, but the user has never encountered
                # it before
                difficulties[entry.chinese] = {
                    "new": True,
                    "score": 10
                }
            else:
                difficulties[entry.chinese] = {
                    "new": False,
                    "score": 10 - mastery.mastery
                }

        word_data = {entry.chinese: {
            "chinese": entry.chinese,
            "english": entry.english,
            "pinyin": entry.pinyin
        } for entry in entries}

        # Calculate the difficulty score of each question, using the word difficulty
        # scores from above
        for question in questions_data:
            difficulty = 0
            new_words = []

            for word in question["words"]:
                if word in difficulties:
                    difficulty += difficulties[word]["score"]

                    if difficulties[word]["new"]:
                        new_words.append(word)
                else:
                    # An entry doesn't exist for this word, we don't know if the
                    # user has encountered it before or not
                    difficulty += 10

            question["difficulty"] = difficulty

            # Get new word data from word_data above and add to the dictionary
            new_words = list(set(new_words))
            question["new_words"] = list(map(lambda x: word_data[x], new_words))

        # Sort questions_data by difficulty scores so we can use binary search
        questions_data.sort(key=lambda x: x["difficulty"])

        # Count how many questions we need to find at random
        num_other_questions = NUM_QUESTIONS - len(question_ids_to_show)

        # Use the normal distribution to calculate the targeted difficulty levels of
        # questions we want to find at random
        difficulties = [math.floor(x) for x in np.random.normal(DIFFICULTY_RNORM_MEAN, DIFFICULTY_RNORM_STDEV, num_other_questions)]

        # Use binary search to find questions that have difficulty scores that match
        # or are closest to the target difficulty scores in the difficulties array
        for difficulty in difficulties:
            if len(questions_data) == 0:
                break

            first = 0
            last = len(questions_data) - 1
            found = False

            while first <= last and not found:
                midpoint = (first + last) // 2

                if questions_data[midpoint]["difficulty"] == difficulty:
                    questions_to_show.append(questions_data[midpoint])
                    found = True

                    # Delete from questions_data so this question is not randomly
                    # picked again later
                    del questions_data[midpoint]
                else:
                    if difficulty < questions_data[midpoint]["difficulty"]:
                        last = midpoint - 1
                    else:
                        first = midpoint + 1

            if not found:
                questions_to_show.append(questions_data[first])

                # Delete from questions_data so this question is not randomly picked
                # again later
                del questions_data[first]

        np.random.shuffle(questions_to_show)

        return questions_to_show
