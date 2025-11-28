// import fetch from 'node-fetch'; // Using native fetch in Node 18+

const API_URL = 'http://localhost:3001/api';

async function verifyMyPosts() {
    try {
        // 1. Login to get token
        console.log('Logging in...');
        const loginResponse = await fetch(`${API_URL}/auth/signin`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: 'telanrc2971@gmail.com',
                password: '9075805070'
            })
        });

        const loginData = await loginResponse.json();
        if (!loginData.token) {
            console.error('Login failed:', loginData);
            return;
        }
        console.log('Login successful. Token received.');

        // 2. Create a post (to ensure there is one)
        console.log('Creating a test post...');
        const createResponse = await fetch(`${API_URL}/activities/posts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${loginData.token}`
            },
            body: JSON.stringify({
                content: 'API Verification Post ' + new Date().toISOString()
            })
        });
        const createData = await createResponse.json();
        console.log('Create post response:', createResponse.status, createData);

        // 3. Fetch My Posts
        console.log('Fetching My Posts...');
        const myPostsResponse = await fetch(`${API_URL}/activities?type=my-posts`, {
            headers: {
                'Authorization': `Bearer ${loginData.token}`
            }
        });

        const myPostsData = await myPostsResponse.json();
        console.log('My Posts response status:', myPostsResponse.status);
        console.log('My Posts data:', JSON.stringify(myPostsData, null, 2));

        if (Array.isArray(myPostsData) && myPostsData.length > 0) {
            console.log('SUCCESS: My Posts endpoint returned data.');
        } else {
            console.error('FAILURE: My Posts endpoint returned empty or invalid data.');
        }

    } catch (error) {
        console.error('Error:', error);
    }
}

verifyMyPosts();
