from app import db, sentry
from app.mod_vocab import Entry
from .models import Mastery

def update_masteries(user_id, correct_words, wrong_words):
    # Populate this updates array to send to update_masteries
    updates = []

    # Loop through all words that were in questions that were answered correctly
    for word in correct_words:
        existing_update_index = None

        # Search for an update if one already exists with this word
        for (idx, update) in enumerate(updates):
            if update["chinese"] == word:
                existing_update_index = idx

        if existing_update_index is not None:
            # Update the existing update if there is one
            updates[existing_update_index]["change"] += 1
        else:
            # Create a new update for this word otherwise
            updates.append({
                "change": 1,
                "chinese": word
            })

    # Loop through all words that were in questions that were answered incorrectly
    for word in wrong_words:
        existing_update_index = None

        # Search for an update if one already exists with this word
        for (idx, update) in enumerate(updates):
            if update["chinese"] == word:
                existing_update_index = idx

        if existing_update_index is not None:
            # Update the existing update if there is one
            updates[existing_update_index]["change"] -= 1
        else:
            # Create a new update for this word otherwise
            updates.append({
                "change": -1,
                "chinese": word
            })

    # Get all words from the updates and convert them to entry ids
    words = [update["chinese"] for update in updates]
    entries = Entry.query.filter(Entry.chinese.in_(words)).all()
    entry_ids = []

    # Add entry ids to the updates with matching Chinese text
    for entry in entries:
        update_index = None

        for (idx, datum) in enumerate(updates):
            if datum["chinese"] == entry.chinese:
                update_index = idx

        entry_ids.append(entry.id)
        updates[update_index]["entry_id"] = entry.id

    # Log any masteries that couldn't find entries to Sentry
    for update in updates:
        if "entry_id" not in update:
            if sentry is not None:
                sentry.captureMessage("Entry could not be found for mastery update: %s" % update["chinese"], extra={
                    "update": update
                })
            else:
                print("Entry could not be found for mastery update: %s" % update["chinese"])

    # Clear all updates that don't have associated entries
    updates = list(filter(lambda x: "entry_id" in x, updates))

    # Find this user's masteries by the entry ids list
    masteries = Mastery.query \
        .filter_by(user_id=user_id) \
        .filter(Mastery.entry_id.in_(entry_ids))

    # Update the mastery value for all of the masteries that already exist
    for mastery in masteries:
        update = None
        update_index = 0

        # Find the update that matches this mastery
        for (idx, datum) in enumerate(updates):
            if datum["entry_id"] == mastery.entry_id:
                update = datum
                update_index = idx

        new_mastery_value = mastery.mastery + update["change"]

        # Make sure the mastery value is 0 ≤ n ≤ 10
        if new_mastery_value < 0:
            new_mastery_value = 0
        elif new_mastery_value > 10:
            new_mastery_value = 10

        mastery.mastery = new_mastery_value

        # Mark this update as done so we know which ones don't have associated masteries
        updates[update_index]["done"] = True

    new_masteries = []

    # Create new masteries for the updates that weren't taken care of earlier
    for update in updates:
        if "done" not in update:
            mastery = Mastery(user_id, update["entry_id"], max(0, update["change"]))
            new_masteries.append(mastery)

    # Add new masteries to the database
    db.session.add_all(new_masteries)

    # Commit new masteries and updates to existing masteries
    db.session.commit()
