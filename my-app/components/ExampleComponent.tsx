import React, { useState, useEffect } from 'react';
import { fetchData, postData } from '../axios/apiClient';

// Define types for our data
interface DataItem {
  id: number;
  title: string;
  description: string;
}

interface PostDataPayload {
  title: string;
  description: string;
}

const ExampleComponent: React.FC = () => {
  // State for storing fetched data
  const [data, setData] = useState<DataItem[] | null>(null);
  // State for loading indicator
  const [loading, setLoading] = useState<boolean>(false);
  // State for error messages
  const [error, setError] = useState<string | null>(null);
  // State for form inputs
  const [formData, setFormData] = useState<PostDataPayload>({
    title: '',
    description: ''
  });

  // Fetch data when component mounts
  useEffect(() => {
    const getData = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await fetchData();
        setData(result);
      } catch (err) {
        setError('Failed to fetch data. Please try again later.');
        console.error('Error fetching data:', err);
      } finally {
        setLoading(false);
      }
    };

    getData();
  }, []);

  // Handle form input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const result = await postData(formData);
      // Add the newly created item to the data array
      if (result && data) {
        setData([...data, result]);
      }
      // Reset form after successful submission
      setFormData({ title: '', description: '' });
    } catch (err) {
      setError('Failed to post data. Please try again later.');
      console.error('Error posting data:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="example-component">
      <h1>Data from API</h1>
      
      {/* Loading state */}
      {loading && <p className="loading">Loading...</p>}
      
      {/* Error message */}
      {error && <p className="error">{error}</p>}

      {/* Display data */}
      {data && data.length > 0 ? (
        <div className="data-container">
          <h2>Fetched Items:</h2>
          <ul>
            {data.map((item) => (
              <li key={item.id} className="data-item">
                <h3>{item.title}</h3>
                <p>{item.description}</p>
              </li>
            ))}
          </ul>
        </div>
      ) : !loading && !error ? (
        <p>No data available.</p>
      ) : null}

      {/* Form for posting new data */}
      <div className="form-container">
        <h2>Add New Item</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="title">Title:</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="description">Description:</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              required
            />
          </div>
          <button 
            type="submit" 
            disabled={loading}
            className="submit-button"
          >
            {loading ? 'Submitting...' : 'Submit'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ExampleComponent;

