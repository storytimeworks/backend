from flask import Blueprint, jsonify, request, session

import json

from app import db
from app.mod_communities.models import Community, Post

mod_communities = Blueprint("communities", __name__, url_prefix="/communities")

@mod_communities.route("", methods=["GET"])
def get_communities():
    communities = Community.query.all()
    communities_data = [community.serialize() for community in communities]
    return jsonify(communities_data)

@mod_communities.route("/<community_id>/posts", methods=["GET"])
def get_posts_for_community(community_id):
    posts = Post.query.filter_by(community=community_id).all()
    posts_data = [post.serialize() for post in posts]
    return jsonify(posts_data)

@mod_communities.route("/posts/<post_id>", methods=["GET"])
def get_posts(post_id):
    post = Post.query.filter_by(id=post_id).first()
    return jsonify(post.serialize())
