# 🌐 Social Network API

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)
![Graph](https://img.shields.io/badge/Data_Structure-Graph-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

[![GitHub stars](https://img.shields.io/github/stars/zain-cs/social-network-api.svg)](https://github.com/zain-cs/social-network-api/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/zain-cs/social-network-api.svg)](https://github.com/zain-cs/social-network-api/network)
[![GitHub issues](https://img.shields.io/github/issues/zain-cs/social-network-api.svg)](https://github.com/zain-cs/social-network-api/issues)

A fully functional **Social Network REST API** built with FastAPI, MySQL, and Graph Data Structures. This project implements intelligent user connection recommendations using graph algorithms like BFS (Breadth-First Search) and provides a complete backend for a modern social media platform.

> 🎓 **Academic Project** - Built as part of learning FastAPI, MySQL, and Data Structures & Algorithms

---

## ✨ Live Demo

🔗 **API Documentation:** `http://localhost:8000/docs` (after running locally)

---

## 🚀 Key Features

### 📱 Social Network Core
- ✅ **User Authentication** - Secure JWT-based authentication system
- ✅ **User Profiles** - Customizable profiles with bio, stats, and activity tracking
- ✅ **Posts & Feed** - Create, edit, delete posts with personalized feed
- ✅ **Comments System** - Multi-level commenting on posts
- ✅ **Like System** - Like/unlike posts and comments
- ✅ **Follow/Unfollow** - Build your social network connections

### 🎯 Graph-Based Intelligence (The Cool Part!)
- 🔍 **Smart Suggestions** - Friend recommendations using "friends of friends" algorithm
- 🔗 **Connection Finder** - Find shortest path between any two users (BFS implementation)
- 👥 **Mutual Connections** - Discover mutual followers and friends
- 📊 **Influencer Detection** - Identify most popular users using graph metrics
- 📈 **Network Analytics** - Real-time network statistics and insights
- ⭐ **Trending Users** - See popular users within your network

---

## 🛠️ Technology Stack

<table>
<tr>
<td>

**Backend Framework**
- FastAPI
- Uvicorn (ASGI server)
- Python 3.8+

</td>
<td>

**Database**
- MySQL 8.0
- SQLAlchemy ORM
- PyMySQL connector

</td>
</tr>
<tr>
<td>

**Security**
- JWT tokens
- Bcrypt hashing
- OAuth2 with Password flow

</td>
<td>

**Data Structures**
- Graph (Adjacency List)
- BFS Algorithm
- Set operations

</td>
</tr>
</table>

---

## 📊 Graph Data Structure Explained

This project uses a **directed graph** to model social relationships efficiently:

### Why Graph?
- **Efficient lookups:** O(1) for checking if user A follows user B
- **Path finding:** BFS algorithm for finding connections
- **Scalable:** Can handle thousands of users and connections
- **Real-world model:** Social networks are naturally graphs!

### Implementation
```python
# Adjacency List Representation
graph = {
    1: [2, 3, 5],    # User 1 follows users 2, 3, 5
    2: [1, 4],       # User 2 follows users 1, 4
    3: [1, 5],       # User 3 follows users 1, 5
    ...
}
```

### Algorithms Used
1. **Breadth-First Search (BFS)**
   - Time Complexity: O(V + E)
   - Use: Finding shortest connection path
   
2. **Set Intersection**
   - Time Complexity: O(min(n, m))
   - Use: Finding mutual connections
   
3. **Graph Traversal**
   - Time Complexity: O(V + E)
   - Use: Community size calculation

---

## 📁 Project Architecture

```
social_network_app/
│
├── 📄 main.py                 # FastAPI app with 40+ endpoints
├── 📄 models.py               # SQLAlchemy database models
├── 📄 schemas.py              # Pydantic validation schemas
├── 📄 database.py             # Database connection config
├── 📄 auth.py                 # JWT authentication logic
├── 📄 graph.py                # Graph DS & algorithms (⭐ Core)
│
├── 🔧 .env                    # Environment variables
├── 🔧 .gitignore             # Git ignore rules
├── 📦 requirements.txt        # Python dependencies
│
├── 📖 README.md              # This file
└── 📖 TESTING_GUIDE.md       # Detailed testing instructions
```

---

## 🗄️ Database Schema

### Entity Relationship Diagram

```
┌─────────┐         ┌─────────┐         ┌──────────┐
│  Users  │────────<│  Posts  │────────<│ Comments │
└─────────┘         └─────────┘         └──────────┘
     │                   │                     │
     │                   │                     │
     └──────┐      ┌─────┘              ┌─────┘
            │      │                     │
      ┌─────▼──────▼─────┐        ┌─────▼──────┐
      │   Post Likes      │        │Comment Likes│
      └───────────────────┘        └────────────┘
            
     ┌─────────┐
     │Followers│ (Self-referencing many-to-many)
     └─────────┘
```

### Tables
| Table | Description |
|-------|-------------|
| `users` | User accounts and profiles |
| `posts` | User-generated content |
| `comments` | Comments on posts |
| `followers` | Follow relationships (graph edges) |
| `post_likes` | Post like relationships |
| `comment_likes` | Comment like relationships |

---

## 🚀 Quick Start Guide

### Prerequisites
- ✅ Python 3.8 or higher
- ✅ MySQL 8.0 or higher
- ✅ Git

### Installation

#### 1️⃣ Clone the Repository
```bash
git clone https://github.com/zain-cs/social-network-api.git
cd social-network-api
```

#### 2️⃣ Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4️⃣ Setup MySQL Database
```sql
-- Login to MySQL command line
mysql -u root -p

-- Create database
CREATE DATABASE fastapi;
EXIT;
```

#### 5️⃣ Configure Environment Variables
Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost/fastapi

# Security (Change these in production!)
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**⚠️ Important:** Replace `YOUR_PASSWORD` with your MySQL password!

#### 6️⃣ Run the Application
```bash
uvicorn main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
✅ Graph loaded: {'total_users': 0, 'total_connections': 0}
```

#### 7️⃣ Access API Documentation
- **Swagger UI (Interactive):** http://localhost:8000/docs
- **ReDoc (Alternative):** http://localhost:8000/redoc

---

## 📚 API Endpoints Reference

### 🔐 Authentication
```
POST   /register          Register new user account
POST   /login             Login and receive JWT token
```

### 👤 User Management
```
GET    /users/me          Get current user profile with stats
PUT    /users/me          Update current user profile
GET    /users             Get all users (paginated)
GET    /users/{id}        Get specific user by ID
GET    /users/search/{username}   Search users by username
```

### 👥 Social Features
```
POST   /users/{id}/follow         Follow a user
DELETE /users/{id}/unfollow       Unfollow a user
GET    /users/{id}/followers      Get user's followers list
GET    /users/{id}/following      Get users that user follows
```

### 📝 Posts & Content
```
POST   /posts                     Create new post
GET    /posts                     Get all posts (paginated)
GET    /posts/{id}                Get specific post
PUT    /posts/{id}                Update own post
DELETE /posts/{id}                Delete own post
GET    /users/{id}/posts          Get all posts by user
GET    /feed                      Get personalized feed
```

### ❤️ Interactions
```
POST   /posts/{id}/like           Like a post
DELETE /posts/{id}/like           Unlike a post
POST   /comments                  Create comment on post
GET    /posts/{id}/comments       Get all comments on post
PUT    /comments/{id}             Update own comment
DELETE /comments/{id}             Delete own comment
POST   /comments/{id}/like        Like a comment
DELETE /comments/{id}/like        Unlike a comment
```

### 🎯 Graph-Based Features (The Magic!)
```
GET    /graph/suggestions         Get friend suggestions (friends of friends)
GET    /graph/connection/{id}     Find shortest path to user
GET    /graph/mutual/{id}         Get mutual connections with user
GET    /graph/influencers         Get most influential users
GET    /graph/network-stats       Get overall network statistics
GET    /graph/popular-in-network  Get trending users in your network
```

---

## 🧪 Testing the API

### Using Swagger UI (Easiest Method)

1. **Start the server** (if not running):
   ```bash
   uvicorn main:app --reload
   ```

2. **Open Swagger UI:**
   - Go to: http://localhost:8000/docs

3. **Register a user:**
   - Find `POST /register`
   - Click "Try it out"
   - Enter user details:
   ```json
   {
     "username": "john_doe",
     "email": "john@example.com",
     "password": "securepass123",
     "full_name": "John Doe",
     "bio": "Hello, I'm John!"
   }
   ```

4. **Login to get token:**
   - Find `POST /login`
   - Enter username and password
   - Copy the `access_token` from response

5. **Authorize:**
   - Click the 🔓 **Authorize** button (top right)
   - Paste: `Bearer YOUR_ACCESS_TOKEN`
   - Click "Authorize"

6. **Test endpoints:**
   - Now you can test any endpoint!
   - Try creating posts, following users, etc.

### Example API Calls with cURL

#### Register User
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "alice123",
    "full_name": "Alice Smith"
  }'
```

#### Login
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=alice123"
```

#### Create Post (Authenticated)
```bash
curl -X POST "http://localhost:8000/posts" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Post",
    "content": "Hello Social Network!",
    "published": true
  }'
```

For detailed step-by-step testing, check [TESTING_GUIDE.md](TESTING_GUIDE.md)

---

## 🎯 Graph Features in Action

### 1. Find Connection Path Between Users

**Request:**
```http
GET /graph/connection/5
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "connected": true,
  "path": ["alice", "bob", "charlie", "david"],
  "degrees_of_separation": 3,
  "is_mutual": false
}
```

### 2. Get Friend Suggestions

**Request:**
```http
GET /graph/suggestions?limit=5
```

**Response:**
```json
[
  {
    "id": 7,
    "username": "emma_wilson",
    "full_name": "Emma Wilson",
    "bio": "Coffee lover ☕"
  },
  {
    "id": 12,
    "username": "mike_tech",
    "full_name": "Mike Johnson",
    "bio": "Tech enthusiast"
  }
]
```

### 3. Network Statistics

**Request:**
```http
GET /graph/network-stats
```

**Response:**
```json
{
  "total_users": 150,
  "total_connections": 487,
  "average_followers": 3.25,
  "your_followers": 12,
  "your_following": 8,
  "your_community_size": 45
}
```

---

## 🔒 Security Features

| Feature | Implementation |
|---------|----------------|
| **Password Security** | Bcrypt hashing with salt |
| **Authentication** | JWT tokens with expiration |
| **Authorization** | Token-based access control |
| **SQL Injection** | Protected via SQLAlchemy ORM |
| **Environment Variables** | Sensitive data in .env (not in repo) |
| **CORS** | Configurable cross-origin settings |

---

## 📈 Performance Considerations

- **In-Memory Graph:** Social graph loaded into memory for O(1) lookups
- **Database Indexing:** Indexes on user IDs, emails, usernames
- **Lazy Loading:** Relationships loaded only when needed
- **Connection Pooling:** Efficient MySQL connection management
- **Pagination:** All list endpoints support pagination

---

## 🎓 What I Learned

Building this project taught me:

✅ **FastAPI Framework** - Modern async Python web framework  
✅ **RESTful API Design** - Best practices for API architecture  
✅ **JWT Authentication** - Secure token-based auth  
✅ **ORM Usage** - SQLAlchemy for database operations  
✅ **Graph Algorithms** - BFS, path finding, network analysis  
✅ **Database Design** - Relational database modeling  
✅ **API Documentation** - Automatic docs with Swagger/OpenAPI  
✅ **Git & GitHub** - Version control and collaboration  

---

## 🚀 Future Enhancements

Features I plan to add:

- [ ] Real-time notifications using WebSockets
- [ ] Direct messaging between users
- [ ] Image upload for posts and profiles (AWS S3)
- [ ] Hashtag system and trending topics
- [ ] Story feature (24-hour posts)
- [ ] User verification badges
- [ ] Advanced search with filters
- [ ] Email notifications
- [ ] Password reset via email
- [ ] Two-factor authentication (2FA)
- [ ] Rate limiting per user
- [ ] Caching with Redis
- [ ] Docker containerization
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Deploy to AWS/Heroku

---

## 🐛 Known Issues & Limitations

- No frontend interface (backend API only)
- Basic error messages (could be more descriptive)
- No email verification on signup
- No password strength validation
- Limited to text posts (no images yet)

**Found a bug?** Please [open an issue](https://github.com/zain-cs/social-network-api/issues)!

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - feel free to use it for learning or your own projects!

---

## 👨‍💻 Author

**Zain**

- 🔗 GitHub: [@zain-cs](https://github.com/zain-cs)
- 📧 Email: [Contact me](mailto:your.email@example.com)
- 💼 LinkedIn: [Connect with me](https://linkedin.com/in/your-profile)

---

## 🙏 Acknowledgments

- Built as an academic project for learning FastAPI and Data Structures
- Thanks to the FastAPI documentation and community
- Inspired by modern social media platforms like Twitter and Instagram
- Special thanks to my instructor for guidance

---

## 📞 Support & Feedback

If you found this project helpful:
- ⭐ Give it a star on GitHub
- 🍴 Fork it and build your own version
- 📢 Share it with others learning FastAPI
- 💬 Open an issue if you have questions

---

## 📸 Screenshots

### Swagger UI Interface
![Swagger UI](https://via.placeholder.com/800x400/4A90E2/ffffff?text=Add+Your+Swagger+UI+Screenshot+Here)

### API Response Example
![API Response](https://via.placeholder.com/800x400/50E3C2/ffffff?text=Add+Your+API+Response+Screenshot+Here)

*Add your own screenshots after deployment!*

---

<div align="center">

**⭐ If you like this project, please give it a star! ⭐**

**Built with ❤️ using FastAPI, MySQL, and Graph Algorithms**

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-blue.svg)](https://www.python.org/)
[![Powered by FastAPI](https://img.shields.io/badge/Powered%20by-FastAPI-green.svg)](https://fastapi.tiangolo.com/)
[![Database MySQL](https://img.shields.io/badge/Database-MySQL-orange.svg)](https://www.mysql.com/)

</div>
