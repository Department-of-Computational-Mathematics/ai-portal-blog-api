"""
Test script to verify authentication system
Run this after starting your FastAPI server
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1/blogs"

def cleanup_test_data(created_items):
    """Clean up test data from the database"""
    print("\n🧹 Cleaning up test data...")
    print("=" * 30)
    
    # Delete in reverse order (replies -> comments -> blogs)
    # This ensures dependencies are handled correctly
    cleanup_order = ["reply", "comment", "blog"]
    
    for item_type in cleanup_order:
        items_to_delete = [item for item in created_items if item["type"] == item_type]
        
        for item in items_to_delete:
            response = None
            try:
                if item_type == "blog":
                    response = requests.delete(f"{BASE_URL}/blogs/{item['id']}", headers=item["headers"])
                elif item_type in ["comment", "reply"]:
                    response = requests.delete(f"{BASE_URL}/delete-comment-reply/{item['id']}", headers=item["headers"])
                
                if response and response.status_code in [200, 204]:
                    print(f"✅ Deleted {item_type} {item['id']}")
                elif response:
                    print(f"⚠️  Failed to delete {item_type} {item['id']}: {response.status_code}")
                else:
                    print(f"❌ No response for {item_type} {item['id']}")
            except Exception as e:
                print(f"❌ Error deleting {item_type} {item['id']}: {e}")
    
    print("🎉 Cleanup completed!")

def test_authentication():
    print("🔐 Testing Authentication System")
    print("=" * 50)
    
    print("\n0. Testing healthcheck...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Healthcheck passed")
    else:
        print("❌ Healthcheck failed")

    # Test data
    user1_id = "user123"
    user2_id = "user456"
    created_items = []  # Track created items for cleanup
      # Test 1: Create blog without authentication (should fail)
    print("\n1. Testing blog creation without authentication...")
    blog_data = {
        "comment_constraint": True,
        "tags": [1, 2],
        "number_of_views": 0,
        "title": "Test Blog",
        "content": "This is a test blog content"
    }
    
    response = requests.post(f"{BASE_URL}/createblog", json=blog_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✅ Correctly rejected - Authentication required")
    else:
        print("❌ Should have been rejected")
    
    # Test 2: Create blog with authentication (should succeed)
    print("\n2. Testing blog creation with authentication...")
    headers = {"X-User-ID": user1_id}
    
    response = requests.post(f"{BASE_URL}/createblog", json=blog_data, headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        blog_id = response.json().get("blogPost_id") or response.json().get("_id")
        created_items.append({"type": "blog", "id": blog_id, "headers": headers})
        print(f"✅ Blog created successfully! ID: {blog_id}")
        
        # Test 3: Try to edit blog with different user (should fail)
        print("\n3. Testing blog edit with different user...")
        headers_user2 = {"X-User-ID": user2_id}
        
        edit_response = requests.put(
            f"{BASE_URL}/updateblog/{blog_id}",
            params={"title": "Hacked Title", "content": "Hacked content", "tags": [1]},
            headers=headers_user2
        )
        print(f"Status: {edit_response.status_code}")
        if edit_response.status_code == 403:
            print("✅ Correctly rejected - Permission denied")
        else:
            print("❌ Should have been rejected")
        
        # Test 4: Edit blog with correct user (should succeed)
        print("\n4. Testing blog edit with correct user...")
        edit_response = requests.put(
            f"{BASE_URL}/updateblog/{blog_id}",
            params={"title": "Updated Title", "content": "Updated content", "tags": [1, 2]},
            headers=headers
        )
        print(f"Status: {edit_response.status_code}")
        if edit_response.status_code == 200:
            print("✅ Blog updated successfully!")
        else:
            print(f"❌ Update failed: {edit_response.text}")
        
        # Test 5: Create a comment on the blog
        print("\n5. Testing comment creation...")
        comment_data = {
            "blogPost_id": blog_id,
            "text": "This is a test comment"
        }
        comment_response = requests.post(f"{BASE_URL}/write-comment", json=comment_data, headers=headers)
        print(f"Comment Status: {comment_response.status_code}")
        if comment_response.status_code == 200:
            comment_id = comment_response.json().get("comment_id") or comment_response.json().get("_id")
            created_items.append({"type": "comment", "id": comment_id, "headers": headers})
            print(f"✅ Comment created successfully! ID: {comment_id}")
            
            # Test 6: Create a reply to the comment
            print("\n6. Testing reply creation...")
            reply_data = {
                "parentContent_id": comment_id,
                "text": "This is a test reply"
            }
            reply_response = requests.post(f"{BASE_URL}/reply-comment", json=reply_data, headers=headers)
            print(f"Reply Status: {reply_response.status_code}")
            if reply_response.status_code == 200:
                reply_id = reply_response.json().get("reply_id") or reply_response.json().get("_id")
                created_items.append({"type": "reply", "id": reply_id, "headers": headers})
                print(f"✅ Reply created successfully! ID: {reply_id}")
                
                # Test 7: Try to edit comment with different user (should fail)
                print("\n7. Testing comment edit with different user...")
                edit_comment_response = requests.put(
                    f"{BASE_URL}/edit-comment-reply/{comment_id}",
                    params={"text": "Hacked comment"},
                    headers=headers_user2
                )
                print(f"Status: {edit_comment_response.status_code}")
                if edit_comment_response.status_code == 403:
                    print("✅ Correctly rejected - Permission denied")
                else:
                    print("❌ Should have been rejected")
                    
            else:
                print(f"❌ Reply creation failed: {reply_response.text}")
        else:
            print(f"❌ Comment creation failed: {comment_response.text}")
            
    else:
        print(f"❌ Blog creation failed: {response.text}")
    
    # Cleanup: Delete all created items
    cleanup_test_data(created_items)

if __name__ == "__main__":
    try:
        test_authentication()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure your FastAPI server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
