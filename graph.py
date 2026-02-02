from typing import List, Set, Dict, Tuple
from collections import deque, defaultdict
import heapq


class SocialGraph:
    """
    Graph data structure for managing social network relationships
    Uses adjacency list representation for efficient operations
    """
    
    def __init__(self):
        self.adjacency_list: Dict[int, List[int]] = {}  # {user_id: [followed_user_ids]}
        self.reverse_adjacency_list: Dict[int, List[int]] = {}  # {user_id: [follower_ids]}
    
    def add_user(self, user_id: int):
        """Add a user node to the graph"""
        if user_id not in self.adjacency_list:
            self.adjacency_list[user_id] = []
            self.reverse_adjacency_list[user_id] = []
    
    def follow_user(self, follower_id: int, followed_id: int):
        """
        Create a directed edge from follower to followed
        Time Complexity: O(1)
        """
        if follower_id not in self.adjacency_list:
            self.add_user(follower_id)
        if followed_id not in self.adjacency_list:
            self.add_user(followed_id)
        
        # Add to adjacency list if not already following
        if followed_id not in self.adjacency_list[follower_id]:
            self.adjacency_list[follower_id].append(followed_id)
            self.reverse_adjacency_list[followed_id].append(follower_id)
    
    def unfollow_user(self, follower_id: int, followed_id: int):
        """
        Remove the directed edge from follower to followed
        Time Complexity: O(n) where n is number of people user follows
        """
        if follower_id in self.adjacency_list:
            if followed_id in self.adjacency_list[follower_id]:
                self.adjacency_list[follower_id].remove(followed_id)
                self.reverse_adjacency_list[followed_id].remove(follower_id)
    
    def get_following(self, user_id: int) -> List[int]:
        """
        Get list of users that user_id follows
        Time Complexity: O(1)
        """
        return self.adjacency_list.get(user_id, [])
    
    def get_followers(self, user_id: int) -> List[int]:
        """
        Get list of users following user_id
        Time Complexity: O(1)
        """
        return self.reverse_adjacency_list.get(user_id, [])
    
    def is_following(self, follower_id: int, followed_id: int) -> bool:
        """Check if follower_id follows followed_id"""
        return followed_id in self.adjacency_list.get(follower_id, [])
    
    def get_mutual_followers(self, user1_id: int, user2_id: int) -> List[int]:
        """
        Find users that both user1 and user2 follow (mutual following)
        Time Complexity: O(n + m) where n and m are following counts
        """
        following1 = set(self.get_following(user1_id))
        following2 = set(self.get_following(user2_id))
        return list(following1.intersection(following2))
    
    def get_mutual_friends(self, user1_id: int, user2_id: int) -> List[int]:
        """
        Find users who follow both user1 and user2 (mutual friends)
        """
        followers1 = set(self.get_followers(user1_id))
        followers2 = set(self.get_followers(user2_id))
        return list(followers1.intersection(followers2))
    
    def suggest_users_to_follow(self, user_id: int, limit: int = 5) -> List[Tuple[int, int]]:
        """
        Suggest users to follow based on:
        1. Friends of friends (people followed by people you follow)
        2. Popularity (users with many followers)
        
        Returns: List of (user_id, score) tuples sorted by score
        Time Complexity: O(n * m) where n is following count and m is avg following per user
        """
        following = set(self.get_following(user_id))
        suggestions = defaultdict(int)
        
        # Find friends of friends and count occurrences (weight by popularity)
        for followed_user in following:
            for potential_follow in self.get_following(followed_user):
                # Don't suggest users already following or self
                if potential_follow != user_id and potential_follow not in following:
                    suggestions[potential_follow] += 1
        
        # Add popularity score (number of followers)
        for suggested_user in suggestions:
            follower_count = len(self.get_followers(suggested_user))
            suggestions[suggested_user] += follower_count * 0.1  # Weight factor
        
        # Sort by score and return top suggestions
        sorted_suggestions = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)
        return sorted_suggestions[:limit]
    
    def shortest_path_bfs(self, start_user: int, end_user: int) -> List[int]:
        """
        Find shortest connection path between two users using BFS
        Time Complexity: O(V + E) where V is vertices and E is edges
        
        Returns: List of user IDs representing the path, empty if no path exists
        """
        if start_user not in self.adjacency_list or end_user not in self.adjacency_list:
            return []
        
        if start_user == end_user:
            return [start_user]
        
        visited = set()
        queue = deque([(start_user, [start_user])])
        
        while queue:
            current_user, path = queue.popleft()
            
            if current_user in visited:
                continue
            
            visited.add(current_user)
            
            # Check all users that current_user follows
            for neighbor in self.adjacency_list.get(current_user, []):
                if neighbor == end_user:
                    return path + [neighbor]
                
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
        
        return []  # No path found
    
    def get_degrees_of_separation(self, user1_id: int, user2_id: int) -> int:
        """
        Calculate degrees of separation between two users
        Returns -1 if no connection exists
        """
        path = self.shortest_path_bfs(user1_id, user2_id)
        if not path:
            return -1
        return len(path) - 1
    
    def get_influencers(self, min_followers: int = 100, limit: int = 10) -> List[Tuple[int, int]]:
        """
        Find most influential users (users with most followers)
        
        Returns: List of (user_id, follower_count) tuples
        """
        influencers = []
        
        for user_id, followers in self.reverse_adjacency_list.items():
            follower_count = len(followers)
            if follower_count >= min_followers:
                influencers.append((user_id, follower_count))
        
        # Sort by follower count
        influencers.sort(key=lambda x: x[1], reverse=True)
        return influencers[:limit]
    
    def get_community_size(self, user_id: int, max_depth: int = 3) -> int:
        """
        Calculate the size of a user's community up to max_depth connections
        Uses BFS to explore the network
        """
        if user_id not in self.adjacency_list:
            return 0
        
        visited = set()
        queue = deque([(user_id, 0)])
        
        while queue:
            current_user, depth = queue.popleft()
            
            if current_user in visited or depth > max_depth:
                continue
            
            visited.add(current_user)
            
            # Explore both following and followers
            for neighbor in self.adjacency_list.get(current_user, []):
                if neighbor not in visited:
                    queue.append((neighbor, depth + 1))
            
            for follower in self.reverse_adjacency_list.get(current_user, []):
                if follower not in visited:
                    queue.append((follower, depth + 1))
        
        return len(visited)
    
    def get_popular_in_network(self, user_id: int, limit: int = 5) -> List[Tuple[int, int]]:
        """
        Find most popular users within the user's network (people they follow)
        
        Returns: List of (user_id, follower_count) tuples
        """
        following = self.get_following(user_id)
        popular_users = []
        
        for followed_user in following:
            follower_count = len(self.get_followers(followed_user))
            popular_users.append((followed_user, follower_count))
        
        popular_users.sort(key=lambda x: x[1], reverse=True)
        return popular_users[:limit]
    
    def detect_mutual_following(self, user1_id: int, user2_id: int) -> bool:
        """Check if two users follow each other (mutual following)"""
        return (self.is_following(user1_id, user2_id) and 
                self.is_following(user2_id, user1_id))
    
    def get_network_stats(self) -> Dict:
        """Get overall network statistics"""
        total_users = len(self.adjacency_list)
        total_connections = sum(len(following) for following in self.adjacency_list.values())
        
        # Calculate average followers per user
        avg_followers = total_connections / total_users if total_users > 0 else 0
        
        return {
            "total_users": total_users,
            "total_connections": total_connections,
            "average_followers": round(avg_followers, 2)
        }