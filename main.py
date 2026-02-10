from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

import models
import schemas
import auth
from database import engine, get_db
from graph import SocialGraph

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Social Network API",
    description="A complete social network with graph-based relationships",
    version="1.0.0"
)

# Initialize social graph
social_graph = SocialGraph()


# Load existing relationships into graph on startup
@app.on_event("startup")
def load_graph():
    """Load all user relationships into the graph structure on startup"""
    db = next(get_db())
    try:
        users = db.query(models.User).all()
        for user in users:
            social_graph.add_user(user.id)
            for followed in user.following:
                social_graph.follow_user(user.id, followed.id)
        
        stats = social_graph.get_network_stats()
        print(f"✅ Graph loaded: {stats}")
    finally:
        db.close()


# ==================== ROOT & HEALTH CHECK ====================

@app.get("/")
def read_root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to Social Network API!",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# ==================== AUTHENTICATION ====================

@app.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if username exists
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        bio=user.bio,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Add user to graph
    social_graph.add_user(db_user.id)
    
    return db_user


@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login to get access token"""
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


# ==================== USER ENDPOINTS ====================

@app.get("/users/me", response_model=schemas.UserWithStats)
def get_current_user_profile(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile with statistics"""
    followers_count = len(social_graph.get_followers(current_user.id))
    following_count = len(social_graph.get_following(current_user.id))
    posts_count = db.query(models.Post).filter(models.Post.author_id == current_user.id).count()
    
    return {
        **current_user.__dict__,
        "followers_count": followers_count,
        "following_count": following_count,
        "posts_count": posts_count
    }


@app.put("/users/me", response_model=schemas.UserResponse)
def update_current_user(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.bio is not None:
        current_user.bio = user_update.bio
    
    db.commit()
    db.refresh(current_user)
    return current_user


@app.get("/users", response_model=List[schemas.UserResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all users (paginated)"""
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=schemas.UserWithStats)
def get_user_by_id(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user by ID with statistics"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    followers_count = len(social_graph.get_followers(user.id))
    following_count = len(social_graph.get_following(user.id))
    posts_count = db.query(models.Post).filter(models.Post.author_id == user.id).count()
    
    return {
        **user.__dict__,
        "followers_count": followers_count,
        "following_count": following_count,
        "posts_count": posts_count
    }


@app.get("/users/search/{username}", response_model=List[schemas.UserResponse])
def search_users(
    username: str,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search users by username"""
    users = db.query(models.User).filter(
        models.User.username.contains(username)
    ).limit(10).all()
    return users


# ==================== FOLLOW/UNFOLLOW ENDPOINTS ====================

@app.post("/users/{user_id}/follow")
def follow_user(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Follow a user"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot follow yourself")
    
    user_to_follow = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_to_follow:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already following
    if user_to_follow in current_user.following:
        raise HTTPException(status_code=400, detail="Already following this user")
    
    # Add to database
    current_user.following.append(user_to_follow)
    db.commit()
    
    # Update graph
    social_graph.follow_user(current_user.id, user_id)
    
    return {
        "message": f"You are now following {user_to_follow.username}",
        "is_mutual": social_graph.detect_mutual_following(current_user.id, user_id)
    }


@app.delete("/users/{user_id}/unfollow")
def unfollow_user(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unfollow a user"""
    user_to_unfollow = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_to_unfollow:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if following
    if user_to_unfollow not in current_user.following:
        raise HTTPException(status_code=400, detail="You are not following this user")
    
    # Remove from database
    current_user.following.remove(user_to_unfollow)
    db.commit()
    
    # Update graph
    social_graph.unfollow_user(current_user.id, user_id)
    
    return {"message": f"You have unfollowed {user_to_unfollow.username}"}


@app.get("/users/{user_id}/followers", response_model=List[schemas.UserResponse])
def get_user_followers(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's followers"""
    follower_ids = social_graph.get_followers(user_id)
    followers = db.query(models.User).filter(models.User.id.in_(follower_ids)).all()
    return followers


@app.get("/users/{user_id}/following", response_model=List[schemas.UserResponse])
def get_user_following(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get users that this user follows"""
    following_ids = social_graph.get_following(user_id)
    following = db.query(models.User).filter(models.User.id.in_(following_ids)).all()
    return following


# ==================== POST ENDPOINTS ====================

@app.post("/posts", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post: schemas.PostCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new post"""
    db_post = models.Post(**post.model_dump(), author_id=current_user.id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    # Add counts
    db_post.likes_count = 0
    db_post.comments_count = 0
    
    return db_post


@app.get("/posts", response_model=List[schemas.PostResponse])
def get_all_posts(
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all posts (paginated)"""
    posts = db.query(models.Post).filter(
        models.Post.published == True
    ).order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()
    
    # Add counts
    for post in posts:
        post.likes_count = len(post.liked_by)
        post.comments_count = len(post.comments)
    
    return posts


@app.get("/posts/{post_id}", response_model=schemas.PostResponse)
def get_post(
    post_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific post"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post.likes_count = len(post.liked_by)
    post.comments_count = len(post.comments)
    
    return post


@app.put("/posts/{post_id}", response_model=schemas.PostResponse)
def update_post(
    post_id: int,
    post_update: schemas.PostUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a post (only by author)"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    
    # Update fields
    if post_update.title is not None:
        post.title = post_update.title
    if post_update.content is not None:
        post.content = post_update.content
    if post_update.image_url is not None:
        post.image_url = post_update.image_url
    if post_update.published is not None:
        post.published = post_update.published
    
    db.commit()
    db.refresh(post)
    
    post.likes_count = len(post.liked_by)
    post.comments_count = len(post.comments)
    
    return post


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a post (only by author)"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    db.delete(post)
    db.commit()
    return None


@app.get("/users/{user_id}/posts", response_model=List[schemas.PostResponse])
def get_user_posts(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all posts by a specific user"""
    posts = db.query(models.Post).filter(
        models.Post.author_id == user_id,
        models.Post.published == True
    ).order_by(models.Post.created_at.desc()).all()
    
    for post in posts:
        post.likes_count = len(post.liked_by)
        post.comments_count = len(post.comments)
    
    return posts


# ==================== LIKE ENDPOINTS ====================

@app.post("/posts/{post_id}/like")
def like_post(
    post_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Like a post"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if current_user in post.liked_by:
        raise HTTPException(status_code=400, detail="Already liked this post")
    
    post.liked_by.append(current_user)
    db.commit()
    
    return {"message": "Post liked successfully", "likes_count": len(post.liked_by)}


@app.delete("/posts/{post_id}/like")
def unlike_post(
    post_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unlike a post"""
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if current_user not in post.liked_by:
        raise HTTPException(status_code=400, detail="You haven't liked this post")
    
    post.liked_by.remove(current_user)
    db.commit()
    
    return {"message": "Post unliked successfully", "likes_count": len(post.liked_by)}


# ==================== COMMENT ENDPOINTS ====================

@app.post("/comments", response_model=schemas.CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment: schemas.CommentCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a comment on a post"""
    post = db.query(models.Post).filter(models.Post.id == comment.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db_comment = models.Comment(
        content=comment.content,
        author_id=current_user.id,
        post_id=comment.post_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    db_comment.likes_count = 0
    
    return db_comment


@app.get("/posts/{post_id}/comments", response_model=List[schemas.CommentResponse])
def get_post_comments(
    post_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all comments for a post"""
    comments = db.query(models.Comment).filter(
        models.Comment.post_id == post_id
    ).order_by(models.Comment.created_at.desc()).all()
    
    for comment in comments:
        comment.likes_count = len(comment.liked_by)
    
    return comments


@app.put("/comments/{comment_id}", response_model=schemas.CommentResponse)
def update_comment(
    comment_id: int,
    comment_update: schemas.CommentUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a comment (only by author)"""
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")
    
    comment.content = comment_update.content
    db.commit()
    db.refresh(comment)
    
    comment.likes_count = len(comment.liked_by)
    
    return comment


@app.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a comment (only by author)"""
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    db.delete(comment)
    db.commit()
    return None


@app.post("/comments/{comment_id}/like")
def like_comment(
    comment_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Like a comment"""
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if current_user in comment.liked_by:
        raise HTTPException(status_code=400, detail="Already liked this comment")
    
    comment.liked_by.append(current_user)
    db.commit()
    
    return {"message": "Comment liked successfully", "likes_count": len(comment.liked_by)}


@app.delete("/comments/{comment_id}/like")
def unlike_comment(
    comment_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unlike a comment"""
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if current_user not in comment.liked_by:
        raise HTTPException(status_code=400, detail="You haven't liked this comment")
    
    comment.liked_by.remove(current_user)
    db.commit()
    
    return {"message": "Comment unliked successfully", "likes_count": len(comment.liked_by)}


# ==================== FEED ENDPOINT ====================

@app.get("/feed", response_model=List[schemas.PostResponse])
def get_feed(
    skip: int = 0,
    limit: int = 20,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get personalized feed (posts from followed users + own posts)"""
    following_ids = social_graph.get_following(current_user.id)
    following_ids.append(current_user.id)  # Include user's own posts
    
    posts = db.query(models.Post).filter(
        models.Post.author_id.in_(following_ids),
        models.Post.published == True
    ).order_by(models.Post.created_at.desc()).offset(skip).limit(limit).all()
    
    for post in posts:
        post.likes_count = len(post.liked_by)
        post.comments_count = len(post.comments)
    
    return posts


# ==================== GRAPH-BASED FEATURES ====================

@app.get("/graph/suggestions", response_model=List[schemas.UserResponse])
def get_user_suggestions(
    limit: int = 5,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user suggestions based on graph algorithms (friends of friends)"""
    suggestions = social_graph.suggest_users_to_follow(current_user.id, limit)
    
    if not suggestions:
        return []
    
    suggested_user_ids = [user_id for user_id, score in suggestions]
    users = db.query(models.User).filter(models.User.id.in_(suggested_user_ids)).all()
    
    # Sort by the original score order
    user_dict = {user.id: user for user in users}
    sorted_users = [user_dict[user_id] for user_id, score in suggestions if user_id in user_dict]
    
    return sorted_users


@app.get("/graph/connection/{user_id}")
def find_connection_path(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Find connection path between current user and another user"""
    if user_id == current_user.id:
        return {"message": "This is you!"}
    
    path = social_graph.shortest_path_bfs(current_user.id, user_id)
    
    if not path:
        return {
            "connected": False,
            "message": "No connection found",
            "degrees_of_separation": -1
        }
    
    # Get usernames for the path
    users = db.query(models.User).filter(models.User.id.in_(path)).all()
    user_dict = {user.id: user.username for user in users}
    path_usernames = [user_dict[uid] for uid in path]
    
    return {
        "connected": True,
        "path": path_usernames,
        "degrees_of_separation": len(path) - 1,
        "is_mutual": social_graph.detect_mutual_following(current_user.id, user_id)
    }


@app.get("/graph/mutual/{user_id}")
def get_mutual_connections(
    user_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get mutual followers between current user and another user"""
    mutual_following = social_graph.get_mutual_followers(current_user.id, user_id)
    mutual_friends = social_graph.get_mutual_friends(current_user.id, user_id)
    
    following_users = db.query(models.User).filter(models.User.id.in_(mutual_following)).all()
    friend_users = db.query(models.User).filter(models.User.id.in_(mutual_friends)).all()
    
    return {
        "mutual_following_count": len(mutual_following),
        "mutual_following": [{"id": u.id, "username": u.username} for u in following_users],
        "mutual_friends_count": len(mutual_friends),
        "mutual_friends": [{"id": u.id, "username": u.username} for u in friend_users]
    }


@app.get("/graph/influencers")
def get_influencers(
    min_followers: int = 10,
    limit: int = 10,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get most influential users (users with most followers)"""
    influencers = social_graph.get_influencers(min_followers, limit)
    
    if not influencers:
        return []
    
    influencer_ids = [user_id for user_id, count in influencers]
    users = db.query(models.User).filter(models.User.id.in_(influencer_ids)).all()
    
    # Create response with follower counts
    user_dict = {user.id: user for user in users}
    result = []
    for user_id, follower_count in influencers:
        if user_id in user_dict:
            user = user_dict[user_id]
            result.append({
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "follower_count": follower_count
            })
    
    return result


@app.get("/graph/network-stats")
def get_network_statistics(
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get overall network statistics"""
    stats = social_graph.get_network_stats()
    
    # Add user-specific stats
    stats["your_followers"] = len(social_graph.get_followers(current_user.id))
    stats["your_following"] = len(social_graph.get_following(current_user.id))
    stats["your_community_size"] = social_graph.get_community_size(current_user.id, max_depth=2)
    
    return stats


@app.get("/graph/popular-in-network")
def get_popular_in_my_network(
    limit: int = 5,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get most popular users within your network"""
    popular = social_graph.get_popular_in_network(current_user.id, limit)
    
    if not popular:
        return []
    
    popular_ids = [user_id for user_id, count in popular]
    users = db.query(models.User).filter(models.User.id.in_(popular_ids)).all()
    
    user_dict = {user.id: user for user in users}
    result = []
    for user_id, follower_count in popular:
        if user_id in user_dict:
            user = user_dict[user_id]
            result.append({
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "follower_count": follower_count
            })
    
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)