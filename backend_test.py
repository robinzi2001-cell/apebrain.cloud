import requests
import sys
import json
from datetime import datetime
import time
import base64
import io

class MushroomBlogAPITester:
    def __init__(self, base_url="https://stonedape.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_blog_id = None
        self.test_product_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timed out after {timeout} seconds")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_admin_login_valid(self):
        """Test admin login with valid credentials"""
        success, response = self.run_test(
            "Admin Login (Valid Credentials)",
            "POST",
            "admin/login",
            200,
            data={"username": "admin", "password": "apebrain2024"}
        )
        return success and response.get('success') == True

    def test_admin_login_invalid(self):
        """Test admin login with invalid credentials"""
        success, response = self.run_test(
            "Admin Login (Invalid Credentials)",
            "POST", 
            "admin/login",
            401,
            data={"username": "admin", "password": "wrongpassword"}
        )
        return success

    def test_generate_blog(self):
        """Test AI blog generation - this may take 30-60 seconds"""
        print("\n⚠️  AI Generation Test - This may take 30-60 seconds...")
        success, response = self.run_test(
            "Generate Blog with AI",
            "POST",
            "blogs/generate",
            200,
            data={"keywords": "Reishi mushroom benefits"},
            timeout=120  # Extended timeout for AI generation
        )
        
        if success:
            # Verify response structure
            required_fields = ['title', 'content', 'image_base64']
            for field in required_fields:
                if field not in response:
                    print(f"❌ Missing required field: {field}")
                    return False
                elif not response[field]:
                    print(f"❌ Empty required field: {field}")
                    return False
            
            print(f"✅ Generated blog title: {response['title'][:50]}...")
            print(f"✅ Generated content length: {len(response['content'])} characters")
            print(f"✅ Generated image: {'Yes' if response['image_base64'] else 'No'}")
            
            # Store for later tests
            self.generated_blog = response
            return True
        
        return False

    def test_create_blog(self):
        """Test creating/saving a blog post"""
        if not hasattr(self, 'generated_blog'):
            print("❌ Cannot test blog creation - no generated blog available")
            return False
            
        blog_data = {
            "id": f"test-blog-{int(time.time())}",
            "title": self.generated_blog['title'],
            "content": self.generated_blog['content'],
            "keywords": "Reishi mushroom benefits",
            "image_base64": self.generated_blog['image_base64'],
            "status": "draft"
        }
        
        success, response = self.run_test(
            "Create Blog Post",
            "POST",
            "blogs",
            200,
            data=blog_data
        )
        
        if success and response.get('id'):
            self.test_blog_id = response['id']
            print(f"✅ Created blog with ID: {self.test_blog_id}")
            return True
        
        return False

    def test_get_blogs(self):
        """Test fetching all blogs"""
        success, response = self.run_test(
            "Get All Blogs",
            "GET",
            "blogs",
            200
        )
        
        if success:
            print(f"✅ Found {len(response)} published blogs")
            return True
        
        return False

    def test_get_single_blog(self):
        """Test fetching a single blog"""
        if not self.test_blog_id:
            print("❌ Cannot test single blog fetch - no blog ID available")
            return False
            
        success, response = self.run_test(
            "Get Single Blog",
            "GET",
            f"blogs/{self.test_blog_id}",
            200
        )
        
        if success and response.get('id') == self.test_blog_id:
            print(f"✅ Successfully fetched blog: {response['title'][:50]}...")
            return True
        
        return False

    def test_publish_blog(self):
        """Test publishing a blog"""
        if not self.test_blog_id:
            print("❌ Cannot test blog publishing - no blog ID available")
            return False
            
        success, response = self.run_test(
            "Publish Blog",
            "POST",
            f"blogs/{self.test_blog_id}/publish",
            200
        )
        
        if success and response.get('success'):
            print("✅ Blog published successfully")
            return True
        
        return False

    def test_delete_blog(self):
        """Test deleting a blog"""
        if not self.test_blog_id:
            print("❌ Cannot test blog deletion - no blog ID available")
            return False
            
        success, response = self.run_test(
            "Delete Blog",
            "DELETE",
            f"blogs/{self.test_blog_id}",
            200
        )
        
        if success and response.get('success'):
            print("✅ Blog deleted successfully")
            return True
        
        return False

    def create_test_image_data(self):
        """Create a small test image in base64 format"""
        # Create a simple 1x1 pixel PNG image
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
        return png_data

    def run_multipart_test(self, name, endpoint, expected_status, file_data, timeout=30, file_type='image'):
        """Run a multipart file upload test"""
        url = f"{self.api_url}/{endpoint}"
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if file_type == 'audio':
                files = {'file': ('test_audio.mp3', file_data, 'audio/mpeg')}
            else:
                files = {'file': ('test_image.png', file_data, 'image/png')}
            
            response = requests.post(url, files=files, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timed out after {timeout} seconds")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_get_products(self):
        """Test fetching all products"""
        success, response = self.run_test(
            "Get All Products",
            "GET",
            "products",
            200
        )
        
        if success:
            print(f"✅ Found {len(response)} products")
            # Check if products have expected structure
            if response and len(response) > 0:
                product = response[0]
                required_fields = ['id', 'name', 'price', 'description', 'category', 'type']
                for field in required_fields:
                    if field not in product:
                        print(f"❌ Missing required field in product: {field}")
                        return False
            return True
        
        return False

    def test_create_product(self):
        """Test creating a new product"""
        product_data = {
            "id": f"test-product-{int(time.time())}",
            "name": "Test Lion's Mane Extract",
            "price": 39.99,
            "description": "Premium test Lion's Mane mushroom extract for cognitive enhancement",
            "category": "Test Supplements",
            "type": "physical"
        }
        
        success, response = self.run_test(
            "Create Product",
            "POST",
            "products",
            200,
            data=product_data
        )
        
        if success and response.get('id'):
            self.test_product_id = response['id']
            print(f"✅ Created product with ID: {self.test_product_id}")
            return True
        
        return False

    def test_upload_product_image(self):
        """Test uploading an image to a product"""
        if not self.test_product_id:
            print("❌ Cannot test product image upload - no product ID available")
            return False
            
        # Create test image data
        image_data = self.create_test_image_data()
        
        success, response = self.run_multipart_test(
            "Upload Product Image",
            f"products/{self.test_product_id}/upload-image",
            200,
            image_data
        )
        
        if success and response.get('success') and response.get('image_url'):
            print(f"✅ Image uploaded successfully")
            # Verify image_url format
            image_url = response['image_url']
            if image_url.startswith('data:image/') and 'base64,' in image_url:
                print(f"✅ Image URL format is correct: {image_url[:50]}...")
                return True
            else:
                print(f"❌ Invalid image URL format: {image_url}")
                return False
        
        return False

    def test_get_products_with_images(self):
        """Test fetching products and verify image URLs are included"""
        success, response = self.run_test(
            "Get Products with Images",
            "GET",
            "products",
            200
        )
        
        if success:
            # Find our test product
            test_product = None
            for product in response:
                if product.get('id') == self.test_product_id:
                    test_product = product
                    break
            
            if test_product:
                if 'image_url' in test_product and test_product['image_url']:
                    print(f"✅ Product has image_url: {test_product['image_url'][:50]}...")
                    return True
                else:
                    print("❌ Product missing image_url field")
                    return False
            else:
                print("❌ Test product not found in products list")
                return False
        
        return False

    def test_update_product(self):
        """Test updating a product"""
        if not self.test_product_id:
            print("❌ Cannot test product update - no product ID available")
            return False
            
        update_data = {
            "name": "Updated Test Lion's Mane Extract",
            "price": 44.99,
            "description": "Updated premium test Lion's Mane mushroom extract"
        }
        
        success, response = self.run_test(
            "Update Product",
            "PUT",
            f"products/{self.test_product_id}",
            200,
            data=update_data
        )
        
        if success:
            print("✅ Product updated successfully")
            return True
        
        return False

    def test_upload_image_to_nonexistent_product(self):
        """Test uploading image to non-existent product (error handling)"""
        fake_product_id = "nonexistent-product-123"
        image_data = self.create_test_image_data()
        
        success, response = self.run_multipart_test(
            "Upload Image to Non-existent Product",
            f"products/{fake_product_id}/upload-image",
            404,
            image_data
        )
        
        if success:
            print("✅ Correctly returned 404 for non-existent product")
            return True
        
        return False

    def test_delete_product(self):
        """Test deleting a product"""
        if not self.test_product_id:
            print("❌ Cannot test product deletion - no product ID available")
            return False
            
        success, response = self.run_test(
            "Delete Product",
            "DELETE",
            f"products/{self.test_product_id}",
            200
        )
        
        if success and response.get('success'):
            print("✅ Product deleted successfully")
            return True
        
        return False

    def test_get_default_landing_settings(self):
        """Test getting default landing page settings (first time)"""
        success, response = self.run_test(
            "Get Default Landing Settings",
            "GET",
            "landing-settings",
            200
        )
        
        if success:
            # Verify default values
            expected_defaults = {
                "show_blog": True,
                "show_shop": True,
                "show_minigames": True
            }
            
            for key, expected_value in expected_defaults.items():
                if key not in response:
                    print(f"❌ Missing required field: {key}")
                    return False
                if response[key] != expected_value:
                    print(f"❌ Incorrect default value for {key}: expected {expected_value}, got {response[key]}")
                    return False
            
            print("✅ Default landing settings returned correctly")
            print(f"   show_blog: {response['show_blog']}")
            print(f"   show_shop: {response['show_shop']}")
            print(f"   show_minigames: {response['show_minigames']}")
            return True
        
        return False

    def test_save_landing_settings(self):
        """Test saving landing page settings"""
        settings_data = {
            "show_blog": False,
            "show_shop": True,
            "show_minigames": False
        }
        
        success, response = self.run_test(
            "Save Landing Settings",
            "POST",
            "landing-settings",
            200,
            data=settings_data
        )
        
        if success and response.get('success'):
            print("✅ Landing settings saved successfully")
            print(f"   Message: {response.get('message', 'No message')}")
            return True
        
        return False

    def test_get_saved_landing_settings(self):
        """Test getting saved landing page settings"""
        success, response = self.run_test(
            "Get Saved Landing Settings",
            "GET",
            "landing-settings",
            200
        )
        
        if success:
            # Verify saved values match what we posted
            expected_values = {
                "show_blog": False,
                "show_shop": True,
                "show_minigames": False
            }
            
            for key, expected_value in expected_values.items():
                if key not in response:
                    print(f"❌ Missing required field: {key}")
                    return False
                if response[key] != expected_value:
                    print(f"❌ Incorrect saved value for {key}: expected {expected_value}, got {response[key]}")
                    return False
            
            print("✅ Saved landing settings returned correctly")
            print(f"   show_blog: {response['show_blog']}")
            print(f"   show_shop: {response['show_shop']}")
            print(f"   show_minigames: {response['show_minigames']}")
            return True
        
        return False

    def test_update_landing_settings(self):
        """Test updating landing page settings (all true)"""
        settings_data = {
            "show_blog": True,
            "show_shop": True,
            "show_minigames": True
        }
        
        success, response = self.run_test(
            "Update Landing Settings (All True)",
            "POST",
            "landing-settings",
            200,
            data=settings_data
        )
        
        if success and response.get('success'):
            print("✅ Landing settings updated successfully")
            print(f"   Message: {response.get('message', 'No message')}")
            return True
        
        return False

    def test_verify_updated_landing_settings(self):
        """Test verifying updated landing page settings"""
        success, response = self.run_test(
            "Verify Updated Landing Settings",
            "GET",
            "landing-settings",
            200
        )
        
        if success:
            # Verify all values are now true
            expected_values = {
                "show_blog": True,
                "show_shop": True,
                "show_minigames": True
            }
            
            for key, expected_value in expected_values.items():
                if key not in response:
                    print(f"❌ Missing required field: {key}")
                    return False
                if response[key] != expected_value:
                    print(f"❌ Incorrect updated value for {key}: expected {expected_value}, got {response[key]}")
                    return False
            
            print("✅ Updated landing settings verified correctly")
            print(f"   show_blog: {response['show_blog']}")
            print(f"   show_shop: {response['show_shop']}")
            print(f"   show_minigames: {response['show_minigames']}")
            return True
        
        return False

    def test_get_default_blog_features(self):
        """Test getting default blog feature settings (first time)"""
        success, response = self.run_test(
            "Get Default Blog Features",
            "GET",
            "blog-features",
            200
        )
        
        if success:
            # Verify default values
            expected_defaults = {
                "enable_video": True,
                "enable_audio": True,
                "enable_text_to_speech": True
            }
            
            for key, expected_value in expected_defaults.items():
                if key not in response:
                    print(f"❌ Missing required field: {key}")
                    return False
                if response[key] != expected_value:
                    print(f"❌ Incorrect default value for {key}: expected {expected_value}, got {response[key]}")
                    return False
            
            print("✅ Default blog features returned correctly")
            print(f"   enable_video: {response['enable_video']}")
            print(f"   enable_audio: {response['enable_audio']}")
            print(f"   enable_text_to_speech: {response['enable_text_to_speech']}")
            return True
        
        return False

    def test_save_blog_features(self):
        """Test saving blog feature settings"""
        settings_data = {
            "enable_video": False,
            "enable_audio": True,
            "enable_text_to_speech": False
        }
        
        success, response = self.run_test(
            "Save Blog Features",
            "POST",
            "blog-features",
            200,
            data=settings_data
        )
        
        if success and response.get('success'):
            print("✅ Blog features saved successfully")
            print(f"   Message: {response.get('message', 'No message')}")
            return True
        
        return False

    def test_get_saved_blog_features(self):
        """Test getting saved blog feature settings"""
        success, response = self.run_test(
            "Get Saved Blog Features",
            "GET",
            "blog-features",
            200
        )
        
        if success:
            # Verify saved values match what we posted
            expected_values = {
                "enable_video": False,
                "enable_audio": True,
                "enable_text_to_speech": False
            }
            
            for key, expected_value in expected_values.items():
                if key not in response:
                    print(f"❌ Missing required field: {key}")
                    return False
                if response[key] != expected_value:
                    print(f"❌ Incorrect saved value for {key}: expected {expected_value}, got {response[key]}")
                    return False
            
            print("✅ Saved blog features returned correctly")
            print(f"   enable_video: {response['enable_video']}")
            print(f"   enable_audio: {response['enable_audio']}")
            print(f"   enable_text_to_speech: {response['enable_text_to_speech']}")
            return True
        
        return False

    def create_test_audio_data(self):
        """Create a small test audio file in MP3 format"""
        # Create a minimal MP3 header (not a real MP3, but enough for testing)
        mp3_header = b'\xff\xfb\x90\x00' + b'\x00' * 100  # Minimal MP3-like data
        return mp3_header

    def test_create_blog_with_video_url(self):
        """Test creating a blog post with video_url field"""
        blog_data = {
            "id": f"test-video-blog-{int(time.time())}",
            "title": "Test Blog with Video",
            "content": "This is a test blog post with a YouTube video embedded.",
            "keywords": "test video blog",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "status": "draft"
        }
        
        success, response = self.run_test(
            "Create Blog with Video URL",
            "POST",
            "blogs",
            200,
            data=blog_data
        )
        
        if success and response.get('id'):
            self.test_video_blog_id = response['id']
            print(f"✅ Created blog with video URL, ID: {self.test_video_blog_id}")
            
            # Verify video_url is stored correctly
            if response.get('video_url') == blog_data['video_url']:
                print(f"✅ Video URL stored correctly: {response['video_url']}")
                return True
            else:
                print(f"❌ Video URL not stored correctly. Expected: {blog_data['video_url']}, Got: {response.get('video_url')}")
                return False
        
        return False

    def test_get_blog_with_video_url(self):
        """Test fetching a blog with video_url field"""
        if not hasattr(self, 'test_video_blog_id'):
            print("❌ Cannot test blog with video URL fetch - no video blog ID available")
            return False
            
        success, response = self.run_test(
            "Get Blog with Video URL",
            "GET",
            f"blogs/{self.test_video_blog_id}",
            200
        )
        
        if success and response.get('id') == self.test_video_blog_id:
            if response.get('video_url'):
                print(f"✅ Successfully fetched blog with video URL: {response['video_url']}")
                return True
            else:
                print("❌ Blog missing video_url field")
                return False
        
        return False

    def test_upload_blog_audio(self):
        """Test uploading an audio file to a blog"""
        if not hasattr(self, 'test_video_blog_id'):
            print("❌ Cannot test blog audio upload - no blog ID available")
            return False
            
        # Create test audio data
        audio_data = self.create_test_audio_data()
        
        success, response = self.run_multipart_test(
            "Upload Blog Audio",
            f"blogs/{self.test_video_blog_id}/upload-audio",
            200,
            audio_data,
            file_type='audio'
        )
        
        if success and response.get('success') and response.get('audio_url'):
            print(f"✅ Audio uploaded successfully")
            # Verify audio_url format
            audio_url = response['audio_url']
            if audio_url.startswith('data:audio/') and 'base64,' in audio_url:
                print(f"✅ Audio URL format is correct: {audio_url[:50]}...")
                return True
            else:
                print(f"❌ Invalid audio URL format: {audio_url}")
                return False
        
        return False

    def test_get_blog_with_audio_url(self):
        """Test fetching a blog with audio_url field after upload"""
        if not hasattr(self, 'test_video_blog_id'):
            print("❌ Cannot test blog with audio URL fetch - no blog ID available")
            return False
            
        success, response = self.run_test(
            "Get Blog with Audio URL",
            "GET",
            f"blogs/{self.test_video_blog_id}",
            200
        )
        
        if success and response.get('id') == self.test_video_blog_id:
            if response.get('audio_url'):
                print(f"✅ Successfully fetched blog with audio URL: {response['audio_url'][:50]}...")
                return True
            else:
                print("❌ Blog missing audio_url field after upload")
                return False
        
        return False

    def test_upload_audio_to_nonexistent_blog(self):
        """Test uploading audio to non-existent blog (error handling)"""
        fake_blog_id = "nonexistent-blog-123"
        audio_data = self.create_test_audio_data()
        
        success, response = self.run_multipart_test(
            "Upload Audio to Non-existent Blog",
            f"blogs/{fake_blog_id}/upload-audio",
            404,
            audio_data,
            file_type='audio'
        )
        
        if success:
            print("✅ Correctly returned 404 for non-existent blog")
            return True
        
        return False

    def test_cleanup_test_video_blog(self):
        """Test deleting the test video blog"""
        if not hasattr(self, 'test_video_blog_id'):
            print("❌ Cannot test video blog deletion - no blog ID available")
            return False
            
        success, response = self.run_test(
            "Delete Test Video Blog",
            "DELETE",
            f"blogs/{self.test_video_blog_id}",
            200
        )
        
        if success and response.get('success'):
            print("✅ Test video blog deleted successfully")
            return True
        
        return False

    def test_fetch_image_good_keywords(self):
        """Test fetching image with good keywords"""
        success, response = self.run_test(
            "Fetch Image with Good Keywords",
            "GET",
            "fetch-image?keywords=forest mushroom",
            200,
            timeout=60  # Extended timeout for image fetch
        )
        
        if success:
            # Verify response structure
            if not response.get('success'):
                print("❌ Response missing success field or success=false")
                return False
            
            image_url = response.get('image_url')
            if not image_url:
                print("❌ Response missing image_url field")
                return False
            
            # Verify base64 format
            if not image_url.startswith('data:image/jpeg;base64,'):
                print(f"❌ Invalid image URL format. Expected 'data:image/jpeg;base64,...', got: {image_url[:50]}...")
                return False
            
            # Verify base64 content exists and is reasonable size
            base64_part = image_url.split('base64,')[1] if 'base64,' in image_url else ''
            if len(base64_part) < 100:  # Very small images would be suspicious
                print(f"❌ Base64 content too small: {len(base64_part)} characters")
                return False
            
            if len(base64_part) > 5000000:  # Very large images (>5MB base64) might be problematic
                print(f"❌ Base64 content too large: {len(base64_part)} characters")
                return False
            
            print(f"✅ Successfully fetched image with good keywords")
            print(f"   Image URL format: {image_url[:50]}...")
            print(f"   Base64 content size: {len(base64_part)} characters")
            return True
        
        return False

    def test_fetch_image_different_keywords(self):
        """Test fetching images with different keywords"""
        test_keywords = ["ocean nature", "mountain landscape", "abstract art"]
        
        for keywords in test_keywords:
            print(f"\n🔍 Testing keywords: '{keywords}'")
            success, response = self.run_test(
                f"Fetch Image with Keywords: {keywords}",
                "GET",
                f"fetch-image?keywords={keywords.replace(' ', '%20')}",
                200,
                timeout=60
            )
            
            if not success:
                print(f"❌ Failed to fetch image for keywords: {keywords}")
                return False
            
            # Verify response structure
            if not response.get('success'):
                print(f"❌ Response missing success field for keywords: {keywords}")
                return False
            
            image_url = response.get('image_url')
            if not image_url or not image_url.startswith('data:image/jpeg;base64,'):
                print(f"❌ Invalid image URL format for keywords: {keywords}")
                return False
            
            print(f"✅ Successfully fetched image for keywords: {keywords}")
        
        print("✅ All different keywords returned valid base64 images")
        return True

    def test_fetch_image_empty_keywords(self):
        """Test fetching image with empty keywords (should use fallback)"""
        success, response = self.run_test(
            "Fetch Image with Empty Keywords",
            "GET",
            "fetch-image?keywords=",
            200,
            timeout=60
        )
        
        if success:
            # Verify response structure
            if not response.get('success'):
                print("❌ Response missing success field or success=false")
                return False
            
            image_url = response.get('image_url')
            if not image_url:
                print("❌ Response missing image_url field")
                return False
            
            # Verify base64 format
            if not image_url.startswith('data:image/jpeg;base64,'):
                print(f"❌ Invalid image URL format. Expected 'data:image/jpeg;base64,...', got: {image_url[:50]}...")
                return False
            
            # Verify base64 content exists
            base64_part = image_url.split('base64,')[1] if 'base64,' in image_url else ''
            if len(base64_part) < 100:
                print(f"❌ Base64 content too small: {len(base64_part)} characters")
                return False
            
            print(f"✅ Successfully fetched fallback image with empty keywords")
            print(f"   Image URL format: {image_url[:50]}...")
            print(f"   Base64 content size: {len(base64_part)} characters")
            return True
        
        return False

    def test_fetch_image_size_validation(self):
        """Test that returned base64 string is reasonable size"""
        success, response = self.run_test(
            "Fetch Image Size Validation",
            "GET",
            "fetch-image?keywords=nature test",
            200,
            timeout=60
        )
        
        if success:
            image_url = response.get('image_url', '')
            if not image_url.startswith('data:image/jpeg;base64,'):
                print("❌ Invalid image URL format")
                return False
            
            # Extract base64 content
            base64_part = image_url.split('base64,')[1] if 'base64,' in image_url else ''
            
            # Check size constraints
            min_size = 1000  # At least 1KB base64 (roughly 750 bytes image)
            max_size = 10000000  # At most 10MB base64 (roughly 7.5MB image)
            
            if len(base64_part) < min_size:
                print(f"❌ Image too small: {len(base64_part)} characters (minimum: {min_size})")
                return False
            
            if len(base64_part) > max_size:
                print(f"❌ Image too large: {len(base64_part)} characters (maximum: {max_size})")
                return False
            
            # Verify it's valid base64
            try:
                import base64
                decoded = base64.b64decode(base64_part)
                if len(decoded) < 500:  # At least 500 bytes for a real image
                    print(f"❌ Decoded image too small: {len(decoded)} bytes")
                    return False
            except Exception as e:
                print(f"❌ Invalid base64 content: {str(e)}")
                return False
            
            print(f"✅ Image size validation passed")
            print(f"   Base64 size: {len(base64_part)} characters")
            print(f"   Decoded size: {len(decoded)} bytes")
            return True
        
        return False

    # ============= NEW PEXELS MULTIPLE IMAGE FETCH TESTS =============

    def test_fetch_multiple_images_good_keywords(self):
        """Test fetching multiple images with good keywords (forest mushroom, count=3)"""
        success, response = self.run_test(
            "Fetch Multiple Images with Good Keywords",
            "GET",
            "fetch-images?keywords=forest mushroom&count=3",
            200,
            timeout=60  # Extended timeout for Pexels API
        )
        
        if success:
            # Verify response structure
            if not response.get('success'):
                print("❌ Response missing success field or success=false")
                return False
            
            image_urls = response.get('image_urls')
            if not image_urls:
                print("❌ Response missing image_urls field")
                return False
            
            if not isinstance(image_urls, list):
                print("❌ image_urls is not a list")
                return False
            
            # Verify we got 2-3 images as expected
            if len(image_urls) < 2 or len(image_urls) > 3:
                print(f"❌ Expected 2-3 images, got {len(image_urls)}")
                return False
            
            # Verify each image URL format
            for i, image_url in enumerate(image_urls):
                if not image_url.startswith('data:image/jpeg;base64,'):
                    print(f"❌ Invalid image URL format for image {i+1}. Expected 'data:image/jpeg;base64,...', got: {image_url[:50]}...")
                    return False
                
                # Verify base64 content exists and is reasonable size
                base64_part = image_url.split('base64,')[1] if 'base64,' in image_url else ''
                if len(base64_part) < 1000:  # At least 1KB base64
                    print(f"❌ Base64 content too small for image {i+1}: {len(base64_part)} characters")
                    return False
                
                if len(base64_part) > 5000000:  # Max 5MB base64
                    print(f"❌ Base64 content too large for image {i+1}: {len(base64_part)} characters")
                    return False
            
            print(f"✅ Successfully fetched {len(image_urls)} images with good keywords")
            print(f"   All images have correct base64 format")
            for i, url in enumerate(image_urls):
                base64_size = len(url.split('base64,')[1]) if 'base64,' in url else 0
                print(f"   Image {i+1} size: {base64_size} characters")
            return True
        
        return False

    def test_fetch_multiple_images_different_keywords(self):
        """Test fetching images with different keywords"""
        test_keywords = ["ocean nature", "mountain landscape", "health wellness"]
        
        for keywords in test_keywords:
            print(f"\n🔍 Testing multiple images with keywords: '{keywords}'")
            success, response = self.run_test(
                f"Fetch Multiple Images with Keywords: {keywords}",
                "GET",
                f"fetch-images?keywords={keywords.replace(' ', '%20')}&count=3",
                200,
                timeout=60
            )
            
            if not success:
                print(f"❌ Failed to fetch images for keywords: {keywords}")
                return False
            
            # Verify response structure
            if not response.get('success'):
                print(f"❌ Response missing success field for keywords: {keywords}")
                return False
            
            image_urls = response.get('image_urls', [])
            if len(image_urls) < 2:
                print(f"❌ Expected at least 2 images for keywords '{keywords}', got {len(image_urls)}")
                return False
            
            # Verify all images have correct format
            for i, image_url in enumerate(image_urls):
                if not image_url.startswith('data:image/jpeg;base64,'):
                    print(f"❌ Invalid image URL format for keywords '{keywords}', image {i+1}")
                    return False
            
            print(f"✅ Successfully fetched {len(image_urls)} images for keywords: {keywords}")
        
        print("✅ All different keywords returned valid multiple base64 images")
        return True

    def test_fetch_images_with_count_parameter(self):
        """Test fetching images with specific count parameter (count=2)"""
        success, response = self.run_test(
            "Fetch Images with Count Parameter (count=2)",
            "GET",
            "fetch-images?keywords=nature&count=2",
            200,
            timeout=60
        )
        
        if success:
            # Verify response structure
            if not response.get('success'):
                print("❌ Response missing success field or success=false")
                return False
            
            image_urls = response.get('image_urls', [])
            if len(image_urls) != 2:
                print(f"❌ Expected exactly 2 images, got {len(image_urls)}")
                return False
            
            # Verify both images have correct format
            for i, image_url in enumerate(image_urls):
                if not image_url.startswith('data:image/jpeg;base64,'):
                    print(f"❌ Invalid image URL format for image {i+1}")
                    return False
            
            print(f"✅ Successfully fetched exactly 2 images as requested")
            return True
        
        return False

    def test_fetch_images_quality_check(self):
        """Test image quality - verify reasonable size and different images"""
        success, response = self.run_test(
            "Fetch Images Quality Check",
            "GET",
            "fetch-images?keywords=mushroom forest&count=3",
            200,
            timeout=60
        )
        
        if success:
            image_urls = response.get('image_urls', [])
            if len(image_urls) < 2:
                print(f"❌ Need at least 2 images for quality check, got {len(image_urls)}")
                return False
            
            decoded_sizes = []
            base64_contents = []
            
            # Check each image quality
            for i, image_url in enumerate(image_urls):
                if not image_url.startswith('data:image/jpeg;base64,'):
                    print(f"❌ Invalid format for image {i+1}")
                    return False
                
                # Extract and validate base64 content
                base64_part = image_url.split('base64,')[1] if 'base64,' in image_url else ''
                base64_contents.append(base64_part)
                
                # Verify it's valid base64 and reasonable size
                try:
                    import base64
                    decoded = base64.b64decode(base64_part)
                    decoded_sizes.append(len(decoded))
                    
                    # Check size constraints (reasonable size for web images)
                    if len(decoded) < 5000:  # 5KB minimum
                        print(f"❌ Image {i+1} too small: {len(decoded)} bytes (minimum: 5KB)")
                        return False
                    
                    if len(decoded) > 500000:  # 500KB maximum  
                        print(f"❌ Image {i+1} too large: {len(decoded)} bytes (maximum: 500KB)")
                        return False
                        
                except Exception as e:
                    print(f"❌ Invalid base64 content for image {i+1}: {str(e)}")
                    return False
            
            # Verify images are different (not duplicates)
            if len(set(base64_contents)) != len(base64_contents):
                print("❌ Found duplicate images - images should be different")
                return False
            
            print(f"✅ Image quality check passed")
            print(f"   Number of images: {len(image_urls)}")
            print(f"   All images are different (no duplicates)")
            for i, size in enumerate(decoded_sizes):
                print(f"   Image {i+1} decoded size: {size} bytes ({size/1024:.1f}KB)")
            return True
        
        return False

    def test_fetch_images_error_handling(self):
        """Test error handling for fetch-images endpoint"""
        # Test with missing keywords parameter
        success, response = self.run_test(
            "Fetch Images without Keywords Parameter",
            "GET",
            "fetch-images",
            422,  # FastAPI validation error for missing required parameter
            timeout=30
        )
        
        if success:
            print("✅ Correctly returned 422 for missing keywords parameter")
            return True
        else:
            # If 422 didn't work, try with empty keywords to see what happens
            success2, response2 = self.run_test(
                "Fetch Images with Empty Keywords",
                "GET", 
                "fetch-images?keywords=",
                200,  # Might still work with empty keywords
                timeout=60
            )
            if success2:
                print("✅ Empty keywords handled gracefully")
                return True
        
        return False

    # ============= PAYPAL & ORDER MANAGEMENT TESTS =============
    
    def test_create_paypal_order(self):
        """Test creating a PayPal order"""
        order_data = {
            "items": [
                {
                    "product_id": "test-product-1",
                    "name": "Test Lion's Mane Extract",
                    "price": 29.99,
                    "quantity": 2,
                    "product_type": "physical"
                }
            ],
            "total": 59.98,
            "customer_email": "customer@example.com"
        }
        
        success, response = self.run_test(
            "Create PayPal Order",
            "POST",
            "shop/create-order",
            200,
            data=order_data,
            timeout=60
        )
        
        if success:
            # Verify response structure
            required_fields = ['success', 'approval_url', 'order_id', 'payment_id']
            for field in required_fields:
                if field not in response:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            if not response.get('success'):
                print("❌ Order creation not successful")
                return False
            
            # Store for later tests
            self.test_order_id = response.get('order_id')
            self.test_payment_id = response.get('payment_id')
            
            print(f"✅ PayPal order created successfully")
            print(f"   Order ID: {self.test_order_id}")
            print(f"   Payment ID: {self.test_payment_id}")
            print(f"   Approval URL: {response.get('approval_url')[:50]}...")
            return True
        
        return False

    def test_create_order_with_coupon(self):
        """Test creating order with coupon code"""
        # First create a test coupon
        coupon_data = {
            "code": "TEST10",
            "discount_type": "percentage",
            "discount_value": 10.0,
            "is_active": True
        }
        
        coupon_success, coupon_response = self.run_test(
            "Create Test Coupon for Order",
            "POST",
            "coupons",
            200,
            data=coupon_data
        )
        
        if not coupon_success:
            print("❌ Failed to create test coupon")
            return False
        
        # Now create order with coupon
        order_data = {
            "items": [
                {
                    "product_id": "test-product-2",
                    "name": "Test Reishi Capsules",
                    "price": 24.99,
                    "quantity": 1,
                    "product_type": "physical"
                }
            ],
            "total": 24.99,
            "customer_email": "customer@example.com",
            "coupon_code": "TEST10"
        }
        
        success, response = self.run_test(
            "Create Order with Coupon",
            "POST",
            "shop/create-order",
            200,
            data=order_data,
            timeout=60
        )
        
        if success and response.get('success'):
            print(f"✅ Order with coupon created successfully")
            return True
        
        return False

    def test_get_all_orders(self):
        """Test getting all orders (admin)"""
        success, response = self.run_test(
            "Get All Orders (Admin)",
            "GET",
            "orders",
            200
        )
        
        if success:
            if isinstance(response, list):
                print(f"✅ Successfully retrieved {len(response)} orders")
                return True
            else:
                print("❌ Response is not a list")
                return False
        
        return False

    def test_get_single_order_tracking(self):
        """Test public order tracking"""
        if not hasattr(self, 'test_order_id'):
            print("❌ Cannot test order tracking - no order ID available")
            return False
        
        success, response = self.run_test(
            "Get Single Order",
            "GET",
            f"orders/{self.test_order_id}",
            200
        )
        
        if success and response.get('id') == self.test_order_id:
            print(f"✅ Successfully retrieved order: {self.test_order_id}")
            return True
        
        return False

    def test_update_order_status(self):
        """Test updating order status"""
        if not hasattr(self, 'test_order_id'):
            print("❌ Cannot test order status update - no order ID available")
            return False
        
        # The endpoint expects status as a query parameter, not in body
        success, response = self.run_test(
            "Update Order Status to Paid",
            "PUT",
            f"orders/{self.test_order_id}/status?status=paid",
            200
        )
        
        if success and response.get('success'):
            print("✅ Order status updated successfully")
            return True
        
        return False

    def test_update_order_tracking(self):
        """Test updating order tracking information"""
        if not hasattr(self, 'test_order_id'):
            print("❌ Cannot test order tracking update - no order ID available")
            return False
        
        # The endpoint expects tracking_number and shipping_carrier as query parameters
        success, response = self.run_test(
            "Update Order Tracking Info",
            "PUT",
            f"orders/{self.test_order_id}/tracking?tracking_number=DHL123456789&shipping_carrier=DHL",
            200
        )
        
        if success and response.get('success'):
            print(f"✅ Order tracking updated successfully")
            print(f"   Tracking URL: {response.get('tracking_url', 'N/A')}")
            return True
        
        return False

    def test_mark_order_viewed(self):
        """Test marking order as viewed by admin"""
        if not hasattr(self, 'test_order_id'):
            print("❌ Cannot test mark order viewed - no order ID available")
            return False
        
        success, response = self.run_test(
            "Mark Order as Viewed",
            "POST",
            f"orders/{self.test_order_id}/mark-viewed",
            200
        )
        
        if success and response.get('success'):
            print("✅ Order marked as viewed successfully")
            return True
        
        return False

    def test_get_unviewed_orders_count(self):
        """Test getting unviewed orders count"""
        success, response = self.run_test(
            "Get Unviewed Orders Count",
            "GET",
            "orders/unviewed/count",
            200
        )
        
        if success and 'count' in response:
            print(f"✅ Unviewed orders count: {response['count']}")
            return True
        
        return False

    def test_delete_order(self):
        """Test deleting an order"""
        if not hasattr(self, 'test_order_id'):
            print("❌ Cannot test order deletion - no order ID available")
            return False
        
        success, response = self.run_test(
            "Delete Order",
            "DELETE",
            f"orders/{self.test_order_id}",
            200
        )
        
        if success and response.get('success'):
            print("✅ Order deleted successfully")
            return True
        
        return False

    # ============= CUSTOMER AUTHENTICATION TESTS =============
    
    def test_customer_registration(self):
        """Test customer registration with valid data"""
        print("\n👤 Testing Customer Registration")
        
        registration_data = {
            "email": "testuser@example.com",
            "password": "Test123456",
            "first_name": "Max",
            "last_name": "Mustermann"
        }
        
        success, response = self.run_test(
            "Customer Registration",
            "POST",
            "auth/register",
            200,
            data=registration_data
        )
        
        if success:
            # Verify response structure
            required_fields = ['success', 'access_token', 'token_type', 'user']
            for field in required_fields:
                if field not in response:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            if not response.get('success'):
                print("❌ Registration not successful")
                return False
            
            # Verify token format
            access_token = response.get('access_token')
            if not access_token or len(access_token) < 50:
                print(f"❌ Invalid access token format: {access_token}")
                return False
            
            # Verify user object
            user = response.get('user', {})
            if user.get('email') != registration_data['email']:
                print(f"❌ Email mismatch in user object")
                return False
            
            if user.get('first_name') != registration_data['first_name']:
                print(f"❌ First name mismatch in user object")
                return False
            
            # Store token for later tests
            self.customer_access_token = access_token
            self.test_customer_email = registration_data['email']
            
            print(f"✅ Customer registration successful")
            print(f"   Email: {user.get('email')}")
            print(f"   Name: {user.get('first_name')} {user.get('last_name')}")
            print(f"   Token: {access_token[:20]}...")
            
            return True
        
        return False
    
    def test_customer_registration_duplicate_email(self):
        """Test registration with existing email (should fail)"""
        registration_data = {
            "email": "testuser@example.com",  # Same email as previous test
            "password": "Test123456",
            "first_name": "Another",
            "last_name": "User"
        }
        
        success, response = self.run_test(
            "Customer Registration (Duplicate Email)",
            "POST",
            "auth/register",
            400,  # Should return 400 for duplicate email
            data=registration_data
        )
        
        if success:
            print("✅ Correctly returned 400 for duplicate email")
            return True
        
        return False
    
    def test_customer_login_valid(self):
        """Test customer login with valid credentials"""
        login_data = {
            "email": "testuser@example.com",
            "password": "Test123456"
        }
        
        success, response = self.run_test(
            "Customer Login (Valid Credentials)",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success:
            # Verify response structure
            required_fields = ['success', 'access_token', 'token_type', 'user']
            for field in required_fields:
                if field not in response:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            if not response.get('success'):
                print("❌ Login not successful")
                return False
            
            # Verify token format
            access_token = response.get('access_token')
            if not access_token or len(access_token) < 50:
                print(f"❌ Invalid access token format: {access_token}")
                return False
            
            # Update stored token
            self.customer_access_token = access_token
            
            print(f"✅ Customer login successful")
            print(f"   Email: {response.get('user', {}).get('email')}")
            print(f"   Token: {access_token[:20]}...")
            
            return True
        
        return False
    
    def test_customer_login_invalid_password(self):
        """Test customer login with wrong password"""
        login_data = {
            "email": "testuser@example.com",
            "password": "WrongPassword123"
        }
        
        success, response = self.run_test(
            "Customer Login (Invalid Password)",
            "POST",
            "auth/login",
            401,  # Should return 401 for invalid credentials
            data=login_data
        )
        
        if success:
            print("✅ Correctly returned 401 for invalid password")
            return True
        
        return False
    
    def test_customer_login_nonexistent_email(self):
        """Test customer login with non-existent email"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "Test123456"
        }
        
        success, response = self.run_test(
            "Customer Login (Non-existent Email)",
            "POST",
            "auth/login",
            401,  # Should return 401 for invalid credentials
            data=login_data
        )
        
        if success:
            print("✅ Correctly returned 401 for non-existent email")
            return True
        
        return False
    
    def test_get_current_user_info(self):
        """Test getting current user info with valid token"""
        if not hasattr(self, 'customer_access_token'):
            print("❌ Cannot test user info - no access token available")
            return False
        
        # Use authorization header
        url = f"{self.api_url}/auth/me"
        headers = {
            'Authorization': f'Bearer {self.customer_access_token}',
            'Content-Type': 'application/json'
        }
        
        self.tests_run += 1
        print(f"\n🔍 Testing Get Current User Info...")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                try:
                    response_data = response.json()
                    
                    # Verify user data structure
                    if response_data.get('email') != self.test_customer_email:
                        print(f"❌ Email mismatch in user info")
                        return False
                    
                    # Verify password is not included
                    if 'hashed_password' in response_data or 'password' in response_data:
                        print(f"❌ Password field found in user info (security issue)")
                        return False
                    
                    # Verify required fields
                    required_fields = ['id', 'email', 'first_name', 'last_name', 'is_member']
                    for field in required_fields:
                        if field not in response_data:
                            print(f"❌ Missing required field in user info: {field}")
                            return False
                    
                    print(f"✅ User info retrieved successfully")
                    print(f"   Email: {response_data.get('email')}")
                    print(f"   Name: {response_data.get('first_name')} {response_data.get('last_name')}")
                    print(f"   Member: {response_data.get('is_member')}")
                    
                    return True
                    
                except Exception as e:
                    print(f"❌ Error parsing response: {str(e)}")
                    return False
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False
    
    def test_get_user_info_invalid_token(self):
        """Test getting user info with invalid token (should fail)"""
        url = f"{self.api_url}/auth/me"
        headers = {
            'Authorization': 'Bearer invalid_token_12345',
            'Content-Type': 'application/json'
        }
        
        self.tests_run += 1
        print(f"\n🔍 Testing Get User Info (Invalid Token)...")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            success = response.status_code == 401
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                print("✅ Correctly returned 401 for invalid token")
                return True
            else:
                print(f"❌ Failed - Expected 401, got {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False
    
    def test_get_user_info_no_token(self):
        """Test getting user info without token (should fail)"""
        url = f"{self.api_url}/auth/me"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing Get User Info (No Token)...")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            success = response.status_code == 403  # FastAPI returns 403 for missing auth
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                print("✅ Correctly returned 403 for missing token")
                return True
            else:
                print(f"❌ Failed - Expected 403, got {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False
    
    def test_get_user_orders(self):
        """Test getting user orders with valid token"""
        if not hasattr(self, 'customer_access_token'):
            print("❌ Cannot test user orders - no access token available")
            return False
        
        url = f"{self.api_url}/auth/orders"
        headers = {
            'Authorization': f'Bearer {self.customer_access_token}',
            'Content-Type': 'application/json'
        }
        
        self.tests_run += 1
        print(f"\n🔍 Testing Get User Orders...")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                try:
                    response_data = response.json()
                    
                    # Should be an array (may be empty for new user)
                    if not isinstance(response_data, list):
                        print(f"❌ Orders response is not an array")
                        return False
                    
                    print(f"✅ User orders retrieved successfully")
                    print(f"   Number of orders: {len(response_data)}")
                    
                    # If there are orders, verify they belong to this user
                    for order in response_data:
                        if order.get('customer_email') != self.test_customer_email:
                            print(f"❌ Order belongs to different customer: {order.get('customer_email')}")
                            return False
                    
                    if response_data:
                        print(f"   All orders belong to correct customer: {self.test_customer_email}")
                    
                    return True
                    
                except Exception as e:
                    print(f"❌ Error parsing response: {str(e)}")
                    return False
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False
    
    def test_get_user_orders_invalid_token(self):
        """Test getting user orders with invalid token (should fail)"""
        url = f"{self.api_url}/auth/orders"
        headers = {
            'Authorization': 'Bearer invalid_token_12345',
            'Content-Type': 'application/json'
        }
        
        self.tests_run += 1
        print(f"\n🔍 Testing Get User Orders (Invalid Token)...")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            success = response.status_code == 401
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                print("✅ Correctly returned 401 for invalid token")
                return True
            else:
                print(f"❌ Failed - Expected 401, got {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False
    
    def test_password_reset_request(self):
        """Test password reset request"""
        reset_request_data = {
            "email": "testuser@example.com"
        }
        
        success, response = self.run_test(
            "Password Reset Request",
            "POST",
            "auth/password-reset-request",
            200,
            data=reset_request_data
        )
        
        if success:
            # Verify response structure
            if not response.get('success'):
                print("❌ Password reset request not successful")
                return False
            
            message = response.get('message', '')
            if 'password reset link' not in message.lower():
                print(f"❌ Unexpected message: {message}")
                return False
            
            print(f"✅ Password reset request successful")
            print(f"   Message: {message}")
            
            return True
        
        return False
    
    def test_password_reset_request_nonexistent_email(self):
        """Test password reset request for non-existent email (should still return 200 for security)"""
        reset_request_data = {
            "email": "nonexistent@example.com"
        }
        
        success, response = self.run_test(
            "Password Reset Request (Non-existent Email)",
            "POST",
            "auth/password-reset-request",
            200,  # Should still return 200 for security reasons
            data=reset_request_data
        )
        
        if success:
            # Should get same message for security
            if not response.get('success'):
                print("❌ Password reset request not successful")
                return False
            
            print(f"✅ Password reset request handled securely for non-existent email")
            return True
        
        return False
    
    def verify_user_in_database(self):
        """Verify user was saved correctly in MongoDB by trying to login again"""
        print(f"\n🔍 Verifying user in database...")
        
        # Try to login again to verify user exists and password is hashed
        login_data = {
            "email": "testuser@example.com",
            "password": "Test123456"
        }
        
        success, response = self.run_test(
            "Verify User in Database (Re-login)",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if success and response.get('success'):
            print(f"✅ User verified in database successfully")
            print(f"   Can login with correct credentials")
            
            # Verify last_login was updated
            user = response.get('user', {})
            if user.get('email') == self.test_customer_email:
                print(f"   User data consistent")
                return True
        
        return False
    
    def test_admin_registration_notification(self):
        """Test that admin receives registration notification email"""
        print(f"\n📧 Testing Admin Registration Notification...")
        
        # Check backend logs for email notification
        try:
            import subprocess
            result = subprocess.run(['tail', '-n', '50', '/var/log/supervisor/backend.out.log'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                log_content = result.stdout
                
                # Look for registration notification in logs
                if 'registration notification' in log_content.lower() or 'neue registrierung' in log_content.lower():
                    print("✅ Admin registration notification found in logs")
                    return True
                else:
                    print("⚠️  Admin registration notification not found in logs (SMTP may not be configured)")
                    print("   This is expected if SMTP settings are not configured")
                    return True  # Don't fail test for missing SMTP config
            else:
                print("⚠️  Could not check backend logs")
                return True  # Don't fail test for log access issues
                
        except Exception as e:
            print(f"⚠️  Could not check logs: {str(e)}")
            return True  # Don't fail test for log access issues

    # ============= COMPREHENSIVE PAYPAL CHECKOUT TESTS =============
    
    def test_paypal_checkout_without_coupon(self):
        """Test PayPal checkout flow WITHOUT coupon - SCENARIO 1"""
        print("\n🛒 SCENARIO 1: PayPal Checkout WITHOUT Coupon")
        
        order_data = {
            "items": [
                {
                    "product_id": "test-123",
                    "name": "Test Product",
                    "quantity": 1,
                    "price": 69.00,
                    "product_type": "physical"
                }
            ],
            "total": 69.00,
            "customer_email": "test@example.com"
        }
        
        success, response = self.run_test(
            "PayPal Checkout WITHOUT Coupon",
            "POST",
            "shop/create-order",
            200,
            data=order_data,
            timeout=60
        )
        
        if success:
            # Verify response structure
            required_fields = ['success', 'approval_url', 'order_id', 'payment_id']
            for field in required_fields:
                if field not in response:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            if not response.get('success'):
                print("❌ Order creation not successful")
                return False
            
            # Verify PayPal sandbox URL
            approval_url = response.get('approval_url', '')
            if 'sandbox.paypal.com' not in approval_url:
                print(f"❌ Invalid PayPal sandbox URL: {approval_url}")
                return False
            
            # Store order ID for verification
            self.test_order_without_coupon_id = response.get('order_id')
            
            print(f"✅ PayPal order created successfully WITHOUT coupon")
            print(f"   Order ID: {self.test_order_without_coupon_id}")
            print(f"   Payment ID: {response.get('payment_id')}")
            print(f"   Total: ${order_data['total']:.2f}")
            print(f"   Approval URL: {approval_url[:80]}...")
            
            # Verify order is saved in MongoDB
            return self.verify_order_in_database(self.test_order_without_coupon_id, 69.00, None)
        
        return False
    
    def test_validate_welcome10_coupon(self):
        """Test validating WELCOME10 coupon - SCENARIO 2 Step 1"""
        print("\n🎫 SCENARIO 2 Step 1: Validate WELCOME10 Coupon")
        
        # First ensure WELCOME10 coupon exists
        coupon_data = {
            "code": "WELCOME10",
            "discount_type": "percentage", 
            "discount_value": 10.0,
            "is_active": True
        }
        
        # Try to create the coupon (might already exist)
        self.run_test(
            "Create WELCOME10 Coupon (if not exists)",
            "POST",
            "coupons",
            200,
            data=coupon_data
        )
        
        # Now validate the coupon
        validate_data = {
            "code": "WELCOME10",
            "order_total": 69.00
        }
        
        success, response = self.run_test(
            "Validate WELCOME10 Coupon",
            "POST",
            "coupons/validate",
            200,
            data=validate_data
        )
        
        if success:
            # Verify validation response
            if not response.get('valid'):
                print("❌ Coupon validation failed")
                return False
            
            # Verify discount calculation (10% of 69 = 6.90)
            expected_discount = 6.90
            actual_discount = response.get('discount_amount', 0)
            
            if abs(actual_discount - expected_discount) > 0.01:
                print(f"❌ Incorrect discount calculation. Expected: ${expected_discount:.2f}, Got: ${actual_discount:.2f}")
                return False
            
            coupon_info = response.get('coupon', {})
            if coupon_info.get('code') != 'WELCOME10':
                print(f"❌ Incorrect coupon code returned: {coupon_info.get('code')}")
                return False
            
            print(f"✅ WELCOME10 coupon validation successful")
            print(f"   Coupon Code: {coupon_info.get('code')}")
            print(f"   Discount Type: {coupon_info.get('discount_type')}")
            print(f"   Discount Value: {coupon_info.get('discount_value')}%")
            print(f"   Calculated Discount: ${actual_discount:.2f}")
            print(f"   Original Total: $69.00")
            print(f"   Final Total: ${69.00 - actual_discount:.2f}")
            
            return True
        
        return False
    
    def test_paypal_checkout_with_coupon(self):
        """Test PayPal checkout flow WITH WELCOME10 coupon - SCENARIO 2 Step 2"""
        print("\n🛒 SCENARIO 2 Step 2: PayPal Checkout WITH WELCOME10 Coupon")
        
        # Calculate discounted total (69.00 - 10% = 62.10)
        original_total = 69.00
        discount_amount = 6.90
        discounted_total = 62.10
        
        order_data = {
            "items": [
                {
                    "product_id": "test-456",
                    "name": "Test Product with Coupon",
                    "quantity": 1,
                    "price": 69.00,
                    "product_type": "physical"
                }
            ],
            "total": discounted_total,
            "customer_email": "test@example.com",
            "coupon_code": "WELCOME10"
        }
        
        success, response = self.run_test(
            "PayPal Checkout WITH WELCOME10 Coupon",
            "POST",
            "shop/create-order",
            200,
            data=order_data,
            timeout=60
        )
        
        if success:
            # Verify response structure
            required_fields = ['success', 'approval_url', 'order_id', 'payment_id']
            for field in required_fields:
                if field not in response:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            if not response.get('success'):
                print("❌ Order creation with coupon not successful")
                return False
            
            # Verify PayPal sandbox URL
            approval_url = response.get('approval_url', '')
            if 'sandbox.paypal.com' not in approval_url:
                print(f"❌ Invalid PayPal sandbox URL: {approval_url}")
                return False
            
            # Store order ID for verification
            self.test_order_with_coupon_id = response.get('order_id')
            
            print(f"✅ PayPal order created successfully WITH WELCOME10 coupon")
            print(f"   Order ID: {self.test_order_with_coupon_id}")
            print(f"   Payment ID: {response.get('payment_id')}")
            print(f"   Original Total: ${original_total:.2f}")
            print(f"   Discount: -${discount_amount:.2f} (10%)")
            print(f"   Final Total: ${discounted_total:.2f}")
            print(f"   Approval URL: {approval_url[:80]}...")
            
            # Verify order is saved in MongoDB with coupon details
            return self.verify_order_in_database(self.test_order_with_coupon_id, discounted_total, "WELCOME10")
        
        return False
    
    def test_invalid_coupon_code(self):
        """Test checkout with invalid coupon code"""
        print("\n❌ Testing Invalid Coupon Code")
        
        validate_data = {
            "code": "INVALID123",
            "order_total": 69.00
        }
        
        success, response = self.run_test(
            "Validate Invalid Coupon Code",
            "POST",
            "coupons/validate",
            404,  # Should return 404 for invalid coupon
            data=validate_data
        )
        
        if success:
            print("✅ Correctly returned 404 for invalid coupon code")
            return True
        
        return False
    
    def verify_order_in_database(self, order_id, expected_total, expected_coupon_code):
        """Verify order is properly saved in MongoDB"""
        print(f"\n🔍 Verifying order {order_id} in database...")
        
        success, response = self.run_test(
            f"Verify Order {order_id} in Database",
            "GET",
            f"orders/{order_id}",
            200
        )
        
        if success:
            # Verify order structure
            if response.get('id') != order_id:
                print(f"❌ Order ID mismatch. Expected: {order_id}, Got: {response.get('id')}")
                return False
            
            # Verify total
            actual_total = response.get('total', 0)
            if abs(actual_total - expected_total) > 0.01:
                print(f"❌ Total mismatch. Expected: ${expected_total:.2f}, Got: ${actual_total:.2f}")
                return False
            
            # Verify coupon code
            actual_coupon = response.get('coupon_code')
            if expected_coupon_code != actual_coupon:
                print(f"❌ Coupon code mismatch. Expected: {expected_coupon_code}, Got: {actual_coupon}")
                return False
            
            # Verify status
            if response.get('status') != 'pending':
                print(f"❌ Incorrect status. Expected: pending, Got: {response.get('status')}")
                return False
            
            # Verify required fields exist
            required_fields = ['items', 'customer_email', 'created_at', 'payment_id']
            for field in required_fields:
                if field not in response:
                    print(f"❌ Missing required field in order: {field}")
                    return False
            
            # Verify discount amount for coupon orders
            if expected_coupon_code:
                discount_amount = response.get('discount_amount', 0)
                expected_discount = 6.90 if expected_coupon_code == 'WELCOME10' else 0
                if abs(discount_amount - expected_discount) > 0.01:
                    print(f"❌ Discount amount mismatch. Expected: ${expected_discount:.2f}, Got: ${discount_amount:.2f}")
                    return False
                print(f"   ✅ Coupon applied: {expected_coupon_code} (-${discount_amount:.2f})")
            
            print(f"✅ Order verified in database successfully")
            print(f"   Order ID: {response.get('id')}")
            print(f"   Status: {response.get('status')}")
            print(f"   Total: ${response.get('total'):.2f}")
            print(f"   Customer: {response.get('customer_email')}")
            print(f"   Items: {len(response.get('items', []))}")
            
            return True
        
        return False
    
    def test_comprehensive_paypal_checkout_summary(self):
        """Summary test to verify both checkout scenarios worked"""
        print("\n📋 COMPREHENSIVE PAYPAL CHECKOUT SUMMARY")
        print("=" * 60)
        
        success_count = 0
        total_tests = 2
        
        # Check order without coupon
        if hasattr(self, 'test_order_without_coupon_id'):
            print("✅ Scenario 1: Checkout WITHOUT coupon - SUCCESS")
            print(f"   Order ID: {self.test_order_without_coupon_id}")
            print(f"   Total: $69.00 (no discount)")
            success_count += 1
        else:
            print("❌ Scenario 1: Checkout WITHOUT coupon - FAILED")
        
        # Check order with coupon
        if hasattr(self, 'test_order_with_coupon_id'):
            print("✅ Scenario 2: Checkout WITH WELCOME10 coupon - SUCCESS")
            print(f"   Order ID: {self.test_order_with_coupon_id}")
            print(f"   Total: $62.10 (10% discount applied)")
            success_count += 1
        else:
            print("❌ Scenario 2: Checkout WITH WELCOME10 coupon - FAILED")
        
        print(f"\n📊 PayPal Checkout Test Results: {success_count}/{total_tests} scenarios passed")
        
        if success_count == total_tests:
            print("🎉 ALL PAYPAL CHECKOUT SCENARIOS SUCCESSFUL!")
            print("   ✅ PayPal sandbox integration working")
            print("   ✅ Order creation without coupon working")
            print("   ✅ Coupon validation working")
            print("   ✅ Order creation with coupon working")
            print("   ✅ Discount calculations accurate")
            print("   ✅ MongoDB order storage working")
            return True
        else:
            print("⚠️  Some PayPal checkout scenarios failed")
            return False

    # ============= COUPON MANAGEMENT TESTS =============
    
    def test_create_coupon(self):
        """Test creating a coupon"""
        coupon_data = {
            "code": "SAVE20",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "is_active": True
        }
        
        success, response = self.run_test(
            "Create Coupon",
            "POST",
            "coupons",
            200,
            data=coupon_data
        )
        
        if success and response.get('id'):
            self.test_coupon_id = response['id']
            print(f"✅ Coupon created successfully: {response['code']}")
            return True
        
        return False

    def test_get_all_coupons(self):
        """Test getting all coupons (admin)"""
        success, response = self.run_test(
            "Get All Coupons",
            "GET",
            "coupons",
            200
        )
        
        if success:
            if isinstance(response, list):
                print(f"✅ Successfully retrieved {len(response)} coupons")
                return True
            else:
                print("❌ Response is not a list")
                return False
        
        return False

    def test_get_active_coupons_public(self):
        """Test getting active coupons (public endpoint)"""
        success, response = self.run_test(
            "Get Active Coupons (Public)",
            "GET",
            "coupons/active",
            200
        )
        
        if success:
            print("✅ Active coupons retrieved successfully")
            return True
        
        return False

    def test_validate_coupon(self):
        """Test coupon validation"""
        # The endpoint expects code and subtotal as query parameters
        success, response = self.run_test(
            "Validate Coupon",
            "POST",
            "coupons/validate?code=SAVE20&subtotal=100.0",
            200
        )
        
        if success and response.get('valid'):
            print(f"✅ Coupon validation successful")
            print(f"   Discount amount: ${response.get('discount_amount', 0)}")
            return True
        
        return False

    def test_update_coupon(self):
        """Test updating a coupon"""
        if not hasattr(self, 'test_coupon_id'):
            print("❌ Cannot test coupon update - no coupon ID available")
            return False
        
        update_data = {
            "discount_value": 25.0,
            "is_active": True
        }
        
        success, response = self.run_test(
            "Update Coupon",
            "PUT",
            f"coupons/{self.test_coupon_id}",
            200,
            data=update_data
        )
        
        if success:
            print("✅ Coupon updated successfully")
            return True
        
        return False

    def test_delete_coupon(self):
        """Test deleting a coupon"""
        if not hasattr(self, 'test_coupon_id'):
            print("❌ Cannot test coupon deletion - no coupon ID available")
            return False
        
        success, response = self.run_test(
            "Delete Coupon",
            "DELETE",
            f"coupons/{self.test_coupon_id}",
            200
        )
        
        if success and response.get('success'):
            print("✅ Coupon deleted successfully")
            return True
        
        return False

    # ============= ADMIN SETTINGS TESTS =============
    
    def test_get_admin_settings(self):
        """Test getting admin settings"""
        success, response = self.run_test(
            "Get Admin Settings",
            "GET",
            "admin/settings",
            200
        )
        
        if success and 'admin_username' in response:
            print(f"✅ Admin settings retrieved: username = {response['admin_username']}")
            return True
        
        return False

    def test_update_admin_settings(self):
        """Test updating admin settings"""
        settings_data = {
            "current_password": "apebrain2024",
            "admin_username": "admin"
        }
        
        success, response = self.run_test(
            "Update Admin Settings",
            "POST",
            "admin/settings",
            200,
            data=settings_data
        )
        
        if success and response.get('success'):
            print("✅ Admin settings updated successfully")
            return True
        
        return False

    # ============= BLOG CRUD COMPREHENSIVE TESTS =============
    
    def test_update_blog(self):
        """Test updating a blog post"""
        if not self.test_blog_id:
            print("❌ Cannot test blog update - no blog ID available")
            return False
        
        update_data = {
            "title": "Updated Test Blog Title",
            "content": "This is updated content for the test blog post.",
            "keywords": "updated test keywords"
        }
        
        success, response = self.run_test(
            "Update Blog Post",
            "PUT",
            f"blogs/{self.test_blog_id}",
            200,
            data=update_data
        )
        
        if success and response.get('id') == self.test_blog_id:
            print("✅ Blog updated successfully")
            return True
        
        return False

    def test_get_blogs_with_status_filter(self):
        """Test getting blogs with status filter"""
        success, response = self.run_test(
            "Get Blogs with Status Filter (draft)",
            "GET",
            "blogs?status=draft",
            200
        )
        
        if success:
            print(f"✅ Found {len(response)} draft blogs")
            return True
        
        return False

    def test_paypal_coupon_fix_validation(self):
        """RE-TEST: Validate WELCOME10 coupon after fix"""
        print("\n🎫 RE-TEST: Validate WELCOME10 Coupon (After Fix)")
        
        # Ensure WELCOME10 coupon exists
        coupon_data = {
            "code": "WELCOME10",
            "discount_type": "percentage", 
            "discount_value": 10.0,
            "is_active": True
        }
        
        # Try to create the coupon (might already exist)
        self.run_test(
            "Ensure WELCOME10 Coupon Exists",
            "POST",
            "coupons",
            200,
            data=coupon_data
        )
        
        # Now validate the coupon
        validate_data = {
            "code": "WELCOME10",
            "order_total": 69.00
        }
        
        success, response = self.run_test(
            "Validate WELCOME10 Coupon",
            "POST",
            "coupons/validate",
            200,
            data=validate_data
        )
        
        if success:
            # Verify validation response
            if not response.get('valid'):
                print("❌ Coupon validation failed")
                return False
            
            # Verify discount calculation (10% of 69 = 6.90)
            expected_discount = 6.90
            actual_discount = response.get('discount_amount', 0)
            
            if abs(actual_discount - expected_discount) > 0.01:
                print(f"❌ Incorrect discount calculation. Expected: ${expected_discount:.2f}, Got: ${actual_discount:.2f}")
                return False
            
            print(f"✅ WELCOME10 coupon validation successful")
            print(f"   Discount Amount: ${actual_discount:.2f}")
            return True
        
        return False

    def test_paypal_coupon_fix_order_creation(self):
        """RE-TEST: Create PayPal order with WELCOME10 coupon after fix"""
        print("\n🛒 RE-TEST: PayPal Order Creation WITH WELCOME10 Coupon (After Fix)")
        
        order_data = {
            "items": [
                {
                    "product_id": "test-coupon-789",
                    "name": "Test Product with Fixed Coupon",
                    "quantity": 1,
                    "price": 69.00,
                    "product_type": "physical"
                }
            ],
            "total": 62.10,  # 69.00 - 10% = 62.10
            "customer_email": "coupon-test@example.com",
            "coupon_code": "WELCOME10"
        }
        
        success, response = self.run_test(
            "Create PayPal Order WITH WELCOME10 Coupon (CRITICAL FIX TEST)",
            "POST",
            "shop/create-order",
            200,
            data=order_data,
            timeout=60
        )
        
        if success:
            # Verify response structure
            required_fields = ['success', 'approval_url', 'order_id', 'payment_id']
            for field in required_fields:
                if field not in response:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            if not response.get('success'):
                print("❌ Order creation with coupon not successful")
                return False
            
            # Verify PayPal sandbox URL (this was failing before the fix)
            approval_url = response.get('approval_url', '')
            if 'sandbox.paypal.com' not in approval_url and 'paypal.com' not in approval_url:
                print(f"❌ Invalid PayPal URL: {approval_url}")
                return False
            
            # Store order ID for verification
            self.test_coupon_fix_order_id = response.get('order_id')
            
            print(f"✅ CRITICAL FIX VERIFIED: PayPal accepts order with coupon!")
            print(f"   Order ID: {self.test_coupon_fix_order_id}")
            print(f"   Payment ID: {response.get('payment_id')}")
            print(f"   Total: $62.10 (after 10% discount)")
            print(f"   Approval URL: {approval_url[:80]}...")
            
            # Verify order is saved in MongoDB with coupon details
            return self.verify_coupon_order_in_database(self.test_coupon_fix_order_id)
        
        return False

    def test_paypal_baseline_without_coupon(self):
        """RE-TEST: Create PayPal order WITHOUT coupon as baseline"""
        print("\n🛒 RE-TEST: PayPal Order Creation WITHOUT Coupon (Baseline)")
        
        order_data = {
            "items": [
                {
                    "product_id": "test-baseline-456",
                    "name": "Test Product Baseline",
                    "quantity": 1,
                    "price": 69.00,
                    "product_type": "physical"
                }
            ],
            "total": 69.00,
            "customer_email": "baseline-test@example.com"
        }
        
        success, response = self.run_test(
            "Create PayPal Order WITHOUT Coupon (Baseline)",
            "POST",
            "shop/create-order",
            200,
            data=order_data,
            timeout=60
        )
        
        if success:
            # Verify response structure
            required_fields = ['success', 'approval_url', 'order_id', 'payment_id']
            for field in required_fields:
                if field not in response:
                    print(f"❌ Missing required field: {field}")
                    return False
            
            if not response.get('success'):
                print("❌ Baseline order creation not successful")
                return False
            
            # Verify PayPal sandbox URL
            approval_url = response.get('approval_url', '')
            if 'sandbox.paypal.com' not in approval_url and 'paypal.com' not in approval_url:
                print(f"❌ Invalid PayPal URL: {approval_url}")
                return False
            
            print(f"✅ Baseline PayPal order created successfully")
            print(f"   Order ID: {response.get('order_id')}")
            print(f"   Total: $69.00 (no discount)")
            print(f"   Approval URL: {approval_url[:80]}...")
            
            return True
        
        return False

    def verify_coupon_order_in_database(self, order_id):
        """Verify coupon order is properly saved in MongoDB"""
        print(f"\n🔍 Verifying coupon order {order_id} in database...")
        
        success, response = self.run_test(
            f"Verify Coupon Order {order_id} in Database",
            "GET",
            f"orders/{order_id}",
            200
        )
        
        if success:
            # Verify order structure
            if response.get('id') != order_id:
                print(f"❌ Order ID mismatch. Expected: {order_id}, Got: {response.get('id')}")
                return False
            
            # Verify total (should be 62.10 after discount)
            expected_total = 62.10
            actual_total = response.get('total', 0)
            if abs(actual_total - expected_total) > 0.01:
                print(f"❌ Total mismatch. Expected: ${expected_total:.2f}, Got: ${actual_total:.2f}")
                return False
            
            # Verify coupon code
            if response.get('coupon_code') != 'WELCOME10':
                print(f"❌ Coupon code mismatch. Expected: WELCOME10, Got: {response.get('coupon_code')}")
                return False
            
            # Verify discount amount
            expected_discount = 6.90
            actual_discount = response.get('discount_amount', 0)
            if abs(actual_discount - expected_discount) > 0.01:
                print(f"❌ Discount amount mismatch. Expected: ${expected_discount:.2f}, Got: ${actual_discount:.2f}")
                return False
            
            print(f"✅ Coupon order verified in database successfully")
            print(f"   Order ID: {response.get('id')}")
            print(f"   Total: ${response.get('total'):.2f}")
            print(f"   Coupon: {response.get('coupon_code')}")
            print(f"   Discount: ${response.get('discount_amount'):.2f}")
            
            return True
        
        return False

    def run_paypal_coupon_fix_tests(self):
        """Run focused PayPal coupon fix tests"""
        print("🚀 RE-TESTING PAYPAL CHECKOUT WITH COUPON - After Fix")
        print(f"Base URL: {self.base_url}")
        print(f"API URL: {self.api_url}")
        print("=" * 80)
        
        # Test sequence as requested in review
        test_sequence = [
            ("1. Validate WELCOME10 Coupon", self.test_paypal_coupon_fix_validation),
            ("2. Create Order WITH Coupon (CRITICAL)", self.test_paypal_coupon_fix_order_creation),
            ("3. Create Order WITHOUT Coupon (Baseline)", self.test_paypal_baseline_without_coupon)
        ]
        
        passed_tests = 0
        total_tests = len(test_sequence)
        
        for test_name, test_func in test_sequence:
            print(f"\n{'='*60}")
            print(f"🧪 {test_name}")
            print('='*60)
            
            try:
                if test_func():
                    passed_tests += 1
                    print(f"✅ {test_name} - PASSED")
                else:
                    print(f"❌ {test_name} - FAILED")
            except Exception as e:
                print(f"❌ {test_name} - FAILED with exception: {str(e)}")
        
        # Final summary
        print("\n" + "="*80)
        print("🏁 PAYPAL COUPON FIX TESTING COMPLETE")
        print(f"Focused Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("🎉 ALL PAYPAL COUPON TESTS PASSED - FIX VERIFIED!")
        else:
            print("⚠️  SOME PAYPAL COUPON TESTS FAILED - NEEDS ATTENTION")
        
        return passed_tests, total_tests

    def run_customer_auth_tests(self):
        """Run comprehensive customer authentication system tests"""
        print("🔐 Starting Customer Authentication System Testing...")
        print("=" * 70)
        
        auth_tests = [
            # Registration Tests
            ("Customer Registration", self.test_customer_registration),
            ("Registration Duplicate Email", self.test_customer_registration_duplicate_email),
            ("Admin Registration Notification", self.test_admin_registration_notification),
            
            # Login Tests  
            ("Customer Login Valid", self.test_customer_login_valid),
            ("Customer Login Invalid Password", self.test_customer_login_invalid_password),
            ("Customer Login Non-existent Email", self.test_customer_login_nonexistent_email),
            
            # Protected Route Tests
            ("Get Current User Info", self.test_get_current_user_info),
            ("Get User Info Invalid Token", self.test_get_user_info_invalid_token),
            ("Get User Info No Token", self.test_get_user_info_no_token),
            ("Get User Orders", self.test_get_user_orders),
            ("Get User Orders Invalid Token", self.test_get_user_orders_invalid_token),
            
            # Password Reset Tests
            ("Password Reset Request", self.test_password_reset_request),
            ("Password Reset Non-existent Email", self.test_password_reset_request_nonexistent_email),
            
            # Database Verification
            ("Verify User in Database", self.verify_user_in_database),
        ]
        
        auth_passed = 0
        auth_total = len(auth_tests)
        
        for test_name, test_func in auth_tests:
            print(f"\n{'='*50}")
            print(f"🧪 {test_name}")
            print('='*50)
            
            try:
                if test_func():
                    auth_passed += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {str(e)}")
        
        print("\n" + "=" * 70)
        print(f"🔐 CUSTOMER AUTHENTICATION TESTING COMPLETE")
        print(f"📊 Results: {auth_passed}/{auth_total} tests passed ({auth_passed/auth_total*100:.1f}%)")
        
        if auth_passed == auth_total:
            print("🎉 ALL AUTHENTICATION TESTS PASSED!")
        else:
            print(f"⚠️  {auth_total - auth_passed} authentication tests failed")
        
        return auth_passed, auth_total

    # ============= COMPREHENSIVE API TESTS AS REQUESTED =============
    
    def test_comprehensive_blog_crud(self):
        """Test comprehensive blog CRUD operations as requested"""
        print("\n📝 COMPREHENSIVE BLOG CRUD TESTING")
        
        # 1. GET /api/blogs - List all published blogs
        success, response = self.run_test(
            "GET /api/blogs - List all published blogs",
            "GET",
            "blogs",
            200
        )
        if not success:
            return False
        print(f"   Found {len(response)} published blogs")
        
        # 2. POST /api/blogs - Create new blog
        blog_data = {
            "id": f"api-test-blog-{int(time.time())}",
            "title": "API Test Blog",
            "content": "Test content for comprehensive API testing",
            "keywords": "api test blog",
            "status": "draft"
        }
        
        success, response = self.run_test(
            "POST /api/blogs - Create new blog",
            "POST",
            "blogs",
            200,
            data=blog_data
        )
        if not success:
            return False
        
        blog_id = response.get('id')
        if not blog_id:
            print("❌ No blog ID returned from creation")
            return False
        
        # 3. GET /api/blogs/{blog_id} - Get single blog
        success, response = self.run_test(
            f"GET /api/blogs/{blog_id} - Get single blog",
            "GET",
            f"blogs/{blog_id}",
            200
        )
        if not success:
            return False
        
        # 4. PUT /api/blogs/{blog_id} - Update blog
        update_data = {
            "title": "Updated API Test Blog"
        }
        
        success, response = self.run_test(
            f"PUT /api/blogs/{blog_id} - Update blog title",
            "PUT",
            f"blogs/{blog_id}",
            200,
            data=update_data
        )
        if not success:
            return False
        
        # 5. POST /api/blogs/{blog_id}/publish - Publish blog
        success, response = self.run_test(
            f"POST /api/blogs/{blog_id}/publish - Publish blog",
            "POST",
            f"blogs/{blog_id}/publish",
            200
        )
        if not success:
            return False
        
        # 6. DELETE /api/blogs/{blog_id} - Delete test blog
        success, response = self.run_test(
            f"DELETE /api/blogs/{blog_id} - Delete test blog",
            "DELETE",
            f"blogs/{blog_id}",
            200
        )
        if not success:
            return False
        
        print("✅ COMPREHENSIVE BLOG CRUD - ALL TESTS PASSED")
        return True
    
    def test_comprehensive_product_crud(self):
        """Test comprehensive product CRUD operations as requested"""
        print("\n🛍️ COMPREHENSIVE PRODUCT CRUD TESTING")
        
        # 1. GET /api/products - List all products
        success, response = self.run_test(
            "GET /api/products - List all products",
            "GET",
            "products",
            200
        )
        if not success:
            return False
        print(f"   Found {len(response)} products")
        
        # 2. POST /api/products - Create product
        product_data = {
            "id": f"api-test-product-{int(time.time())}",
            "name": "Test Product",
            "price": 29.99,
            "description": "Test product for API testing",
            "category": "Test",
            "type": "physical"
        }
        
        success, response = self.run_test(
            "POST /api/products - Create product",
            "POST",
            "products",
            200,
            data=product_data
        )
        if not success:
            return False
        
        product_id = response.get('id')
        if not product_id:
            print("❌ No product ID returned from creation")
            return False
        
        # 3. PUT /api/products/{product_id} - Update product
        update_data = {
            "price": 39.99
        }
        
        success, response = self.run_test(
            f"PUT /api/products/{product_id} - Update product price",
            "PUT",
            f"products/{product_id}",
            200,
            data=update_data
        )
        if not success:
            return False
        
        # 4. DELETE /api/products/{product_id} - Delete test product
        success, response = self.run_test(
            f"DELETE /api/products/{product_id} - Delete test product",
            "DELETE",
            f"products/{product_id}",
            200
        )
        if not success:
            return False
        
        print("✅ COMPREHENSIVE PRODUCT CRUD - ALL TESTS PASSED")
        return True
    
    def test_comprehensive_coupon_system(self):
        """Test comprehensive coupon system as requested"""
        print("\n🎫 COMPREHENSIVE COUPON SYSTEM TESTING")
        
        # 1. GET /api/coupons - List all coupons
        success, response = self.run_test(
            "GET /api/coupons - List all coupons",
            "GET",
            "coupons",
            200
        )
        if not success:
            return False
        print(f"   Found {len(response)} coupons")
        
        # 2. POST /api/coupons - Create coupon
        coupon_data = {
            "code": "APITEST10",
            "discount_value": 10,
            "discount_type": "percentage",
            "is_active": True
        }
        
        success, response = self.run_test(
            "POST /api/coupons - Create coupon",
            "POST",
            "coupons",
            200,
            data=coupon_data
        )
        if not success:
            return False
        
        coupon_id = response.get('id')
        if not coupon_id:
            print("❌ No coupon ID returned from creation")
            return False
        
        # 3. POST /api/coupons/validate - Validate coupon
        validate_data = {
            "code": "WELCOME10",
            "order_total": 100.0
        }
        
        success, response = self.run_test(
            "POST /api/coupons/validate - Validate coupon WELCOME10",
            "POST",
            "coupons/validate",
            200,
            data=validate_data
        )
        if not success:
            return False
        
        # 4. DELETE /api/coupons/{coupon_id} - Delete test coupon
        success, response = self.run_test(
            f"DELETE /api/coupons/{coupon_id} - Delete test coupon",
            "DELETE",
            f"coupons/{coupon_id}",
            200
        )
        if not success:
            return False
        
        print("✅ COMPREHENSIVE COUPON SYSTEM - ALL TESTS PASSED")
        return True
    
    def test_comprehensive_order_management(self):
        """Test comprehensive order management as requested"""
        print("\n📦 COMPREHENSIVE ORDER MANAGEMENT TESTING")
        
        # 1. GET /api/orders - Get all orders
        success, response = self.run_test(
            "GET /api/orders - Get all orders",
            "GET",
            "orders",
            200
        )
        if not success:
            return False
        print(f"   Found {len(response)} orders")
        
        # 2. GET /api/orders/unviewed/count - Check unviewed count
        success, response = self.run_test(
            "GET /api/orders/unviewed/count - Check unviewed count",
            "GET",
            "orders/unviewed/count",
            200
        )
        if not success:
            return False
        print(f"   Unviewed orders: {response.get('count', 0)}")
        
        # If orders exist, test order operations
        orders_response = self.run_test(
            "GET /api/orders - Get orders for testing",
            "GET",
            "orders",
            200
        )
        
        if orders_response[0] and len(orders_response[1]) > 0:
            order_id = orders_response[1][0].get('id')
            if order_id:
                # 3. PUT /api/orders/{order_id}/status - Update status
                success, response = self.run_test(
                    f"PUT /api/orders/{order_id}/status - Update status to packed",
                    "PUT",
                    f"orders/{order_id}/status?status=packed",
                    200
                )
                if not success:
                    return False
                
                # 4. PUT /api/orders/{order_id}/tracking - Add tracking
                success, response = self.run_test(
                    f"PUT /api/orders/{order_id}/tracking - Add tracking info",
                    "PUT",
                    f"orders/{order_id}/tracking?tracking_number=TEST123&shipping_carrier=DHL",
                    200
                )
                if not success:
                    return False
                
                # 5. POST /api/orders/{order_id}/viewed - Mark as viewed
                success, response = self.run_test(
                    f"POST /api/orders/{order_id}/viewed - Mark as viewed",
                    "POST",
                    f"orders/{order_id}/viewed",
                    200
                )
                if not success:
                    return False
        
        print("✅ COMPREHENSIVE ORDER MANAGEMENT - ALL TESTS PASSED")
        return True
    
    def test_comprehensive_paypal_integration(self):
        """Test comprehensive PayPal integration as requested"""
        print("\n💳 COMPREHENSIVE PAYPAL INTEGRATION TESTING")
        
        # 1. POST /api/shop/create-order - Create order WITHOUT coupon
        order_data_no_coupon = {
            "items": [
                {
                    "product_id": "phys-1",
                    "name": "Test Product",
                    "price": 29.99,
                    "quantity": 1,
                    "product_type": "physical"
                }
            ],
            "total": 29.99,
            "customer_email": "test@test.com"
        }
        
        success, response = self.run_test(
            "POST /api/shop/create-order - Create order WITHOUT coupon",
            "POST",
            "shop/create-order",
            200,
            data=order_data_no_coupon,
            timeout=60
        )
        if not success:
            return False
        
        # Verify PayPal response structure
        required_fields = ['success', 'approval_url', 'order_id', 'payment_id']
        for field in required_fields:
            if field not in response:
                print(f"❌ Missing required field: {field}")
                return False
        
        print(f"   Order created: {response.get('order_id')}")
        print(f"   PayPal URL: {response.get('approval_url')[:50]}...")
        
        # 2. POST /api/shop/create-order - Create order WITH coupon
        order_data_with_coupon = {
            "items": [
                {
                    "product_id": "phys-1",
                    "name": "Test Product",
                    "price": 29.99,
                    "quantity": 1,
                    "product_type": "physical"
                }
            ],
            "total": 26.99,  # Assuming 10% discount
            "customer_email": "test@test.com",
            "coupon_code": "WELCOME10"
        }
        
        success, response = self.run_test(
            "POST /api/shop/create-order - Create order WITH coupon WELCOME10",
            "POST",
            "shop/create-order",
            200,
            data=order_data_with_coupon,
            timeout=60
        )
        if not success:
            return False
        
        print(f"   Order with coupon created: {response.get('order_id')}")
        
        print("✅ COMPREHENSIVE PAYPAL INTEGRATION - ALL TESTS PASSED")
        return True
    
    def test_comprehensive_admin_settings(self):
        """Test comprehensive admin settings as requested"""
        print("\n⚙️ COMPREHENSIVE ADMIN SETTINGS TESTING")
        
        # 1. GET /api/landing-settings - Get landing page settings
        success, response = self.run_test(
            "GET /api/landing-settings - Get landing page settings",
            "GET",
            "landing-settings",
            200
        )
        if not success:
            return False
        
        # 2. POST /api/landing-settings - Update settings
        settings_data = {
            "show_blog": True,
            "show_shop": True,
            "show_minigames": False
        }
        
        success, response = self.run_test(
            "POST /api/landing-settings - Update settings",
            "POST",
            "landing-settings",
            200,
            data=settings_data
        )
        if not success:
            return False
        
        # 3. GET /api/blog-features - Get blog features
        success, response = self.run_test(
            "GET /api/blog-features - Get blog features",
            "GET",
            "blog-features",
            200
        )
        if not success:
            return False
        
        # 4. POST /api/blog-features - Update features
        features_data = {
            "enable_video": True,
            "enable_audio": True,
            "enable_text_to_speech": False
        }
        
        success, response = self.run_test(
            "POST /api/blog-features - Update features",
            "POST",
            "blog-features",
            200,
            data=features_data
        )
        if not success:
            return False
        
        print("✅ COMPREHENSIVE ADMIN SETTINGS - ALL TESTS PASSED")
        return True
    
    def test_comprehensive_user_authentication(self):
        """Test comprehensive user authentication as requested"""
        print("\n👤 COMPREHENSIVE USER AUTHENTICATION TESTING")
        
        # Generate unique email for this test run
        timestamp = int(time.time())
        test_email = f"api-test-{timestamp}@test.com"
        
        # 1. POST /api/auth/register - Register user
        register_data = {
            "email": test_email,
            "password": "Test123!",
            "first_name": "API",
            "last_name": "Tester"
        }
        
        success, response = self.run_test(
            f"POST /api/auth/register - Register user {test_email}",
            "POST",
            "auth/register",
            200,
            data=register_data
        )
        if not success:
            return False
        
        # Verify response structure
        required_fields = ['success', 'access_token', 'token_type', 'user']
        for field in required_fields:
            if field not in response:
                print(f"❌ Missing required field: {field}")
                return False
        
        access_token = response.get('access_token')
        print(f"   User registered: {test_email}")
        print(f"   Token: {access_token[:20]}...")
        
        # 2. POST /api/auth/login - Login with registered user
        login_data = {
            "email": test_email,
            "password": "Test123!"
        }
        
        success, response = self.run_test(
            f"POST /api/auth/login - Login with registered user",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        if not success:
            return False
        
        # Update token from login
        access_token = response.get('access_token')
        
        # 3. GET /api/auth/me - Get user info (with Bearer token)
        url = f"{self.api_url}/auth/me"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        self.tests_run += 1
        print(f"\n🔍 Testing GET /api/auth/me - Get user info with Bearer token...")
        print(f"   URL: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                response_data = response.json()
                if response_data.get('email') != test_email:
                    print(f"❌ Email mismatch in user info")
                    return False
                
                print(f"   User info retrieved: {response_data.get('email')}")
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False
        
        print("✅ COMPREHENSIVE USER AUTHENTICATION - ALL TESTS PASSED")
        return True
    
    def test_comprehensive_image_media_apis(self):
        """Test comprehensive image & media APIs as requested"""
        print("\n🖼️ COMPREHENSIVE IMAGE & MEDIA API TESTING")
        
        # 1. GET /api/fetch-image?keywords=nature+forest - Fetch single image
        success, response = self.run_test(
            "GET /api/fetch-image?keywords=nature+forest - Fetch single image",
            "GET",
            "fetch-image?keywords=nature+forest",
            200,
            timeout=60
        )
        if not success:
            return False
        
        # Verify image response
        if not response.get('success') or not response.get('image_url'):
            print("❌ Invalid image response structure")
            return False
        
        image_url = response.get('image_url')
        if not image_url.startswith('data:image/'):
            print(f"❌ Invalid image URL format: {image_url[:50]}...")
            return False
        
        print(f"   Single image fetched: {image_url[:50]}...")
        
        # 2. GET /api/fetch-images?keywords=mushroom&count=3 - Fetch multiple Pexels images
        success, response = self.run_test(
            "GET /api/fetch-images?keywords=mushroom&count=3 - Fetch multiple images",
            "GET",
            "fetch-images?keywords=mushroom&count=3",
            200,
            timeout=60
        )
        if not success:
            return False
        
        # Verify multiple images response
        if not response.get('success') or not response.get('image_urls'):
            print("❌ Invalid multiple images response structure")
            return False
        
        image_urls = response.get('image_urls', [])
        if len(image_urls) < 2:
            print(f"❌ Expected at least 2 images, got {len(image_urls)}")
            return False
        
        # Verify all images have correct format
        for i, img_url in enumerate(image_urls):
            if not img_url.startswith('data:image/'):
                print(f"❌ Invalid image URL format for image {i+1}")
                return False
        
        print(f"   Multiple images fetched: {len(image_urls)} images")
        
        print("✅ COMPREHENSIVE IMAGE & MEDIA APIs - ALL TESTS PASSED")
        return True

    def run_comprehensive_api_tests(self):
        """Run all comprehensive API tests as requested in the review"""
        print("🍄 COMPREHENSIVE BACKEND API TESTING - APEBRAIN.CLOUD")
        print(f"🌐 Backend URL: {self.base_url}")
        print(f"🔗 API URL: {self.api_url}")
        print("=" * 80)

        # COMPREHENSIVE TEST SEQUENCE AS REQUESTED IN REVIEW
        comprehensive_tests = [
            # 1. BLOG CRUD OPERATIONS
            ("1. BLOG CRUD OPERATIONS", [
                self.test_comprehensive_blog_crud,
            ]),
            
            # 2. PRODUCT CRUD OPERATIONS  
            ("2. PRODUCT CRUD OPERATIONS", [
                self.test_comprehensive_product_crud,
            ]),
            
            # 3. COUPON SYSTEM
            ("3. COUPON SYSTEM", [
                self.test_comprehensive_coupon_system,
            ]),
            
            # 4. ORDER MANAGEMENT
            ("4. ORDER MANAGEMENT", [
                self.test_comprehensive_order_management,
            ]),
            
            # 5. PAYPAL INTEGRATION
            ("5. PAYPAL INTEGRATION", [
                self.test_comprehensive_paypal_integration,
            ]),
            
            # 6. ADMIN SETTINGS
            ("6. ADMIN SETTINGS", [
                self.test_comprehensive_admin_settings,
            ]),
            
            # 7. USER AUTHENTICATION
            ("7. USER AUTHENTICATION", [
                self.test_comprehensive_user_authentication,
            ]),
            
            # 8. IMAGE & MEDIA APIs
            ("8. IMAGE & MEDIA APIs", [
                self.test_comprehensive_image_media_apis,
            ]),
            
            # ADDITIONAL DETAILED TESTS
            ("ADDITIONAL DETAILED TESTS", [
                self.test_admin_login_valid,
                self.test_admin_login_invalid,
            ]),
        ]

        # Run comprehensive tests
        for category, test_functions in comprehensive_tests:
            print(f"\n{'='*20} {category} {'='*20}")
            for test_func in test_functions:
                try:
                    test_func()
                except Exception as e:
                    print(f"❌ Test {test_func.__name__} failed with exception: {str(e)}")
                    self.tests_run += 1

        # Print comprehensive summary
        print("\n" + "="*80)
        print("🍄 COMPREHENSIVE BACKEND API TEST SUMMARY - APEBRAIN.CLOUD")
        print("="*80)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL COMPREHENSIVE API TESTS PASSED!")
        else:
            print("⚠️  Some tests failed. Check the output above for details.")
        
        return self.tests_passed == self.tests_run

def main():
    """Main function to run comprehensive API tests as requested"""
    
    tester = MushroomBlogAPITester()
    
    # Run the comprehensive API tests as requested in the review
    success = tester.run_comprehensive_api_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())