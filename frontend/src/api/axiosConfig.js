import axios from 'axios';

const api = axios.create({
    baseURL: 'http://127.0.0.1:5000',
    withCredentials: true, // IMPORTANT: Allows cookies to be sent/received
    headers: {
        'Content-Type': 'application/json',
    },
});

export default api;