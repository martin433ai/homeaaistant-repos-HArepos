import axios from 'axios';

// Making a GET request
const fetchData = async () => {
  try {
    const response = await axios.get('https://api.example.com/data');
    console.log(response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching data:', error);
  }
};

// Making a POST request
const postData = async (data) => {
  try {
    const response = await axios.post('https://api.example.com/data', data);
    return response.data;
  } catch (error) {
    console.error('Error posting data:', error);
  }
};

export { fetchData, postData };

