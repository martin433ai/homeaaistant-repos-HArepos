import axios from 'axios';
import https from 'https';

/**
 * Axios instance configured for Home Assistant API
 * Based on configuration from /Users/martinpark/.config/hass-cli/config.json
 */

// Configure axios with Home Assistant settings
const homeAssistantApi = axios.create({
  baseURL: 'https://homeassistant.local:8123',
  timeout: 15000, // 15 seconds as specified in config
  headers: {
    'Authorization': 'Bearer 2xiXSshhpZYeCjcwc2gIKaVpqNFh564JP27CqI',
    'Content-Type': 'application/json',
  },
  // Disable SSL verification as specified in config
  httpsAgent: new https.Agent({
    rejectUnauthorized: false
  })
});

/**
 * Error handler function to format and log errors
 * @param {Error} error - The error object
 * @returns {Object} Formatted error object
 */
const handleError = (error) => {
  let errorMessage = 'Unknown error occurred';
  let errorDetails = {};

  if (error.response) {
    // Server responded with a status code outside of 2xx range
    errorMessage = `Server error: ${error.response.status}`;
    errorDetails = {
      status: error.response.status,
      statusText: error.response.statusText,
      data: error.response.data
    };
    console.error('Response error:', errorMessage, errorDetails);
  } else if (error.request) {
    // Request was made but no response received
    errorMessage = 'No response received from Home Assistant';
    errorDetails = { request: error.request };
    console.error('Request error:', errorMessage);
  } else {
    // Error in setting up the request
    errorMessage = error.message;
    console.error('Error:', errorMessage);
  }

  return { message: errorMessage, details: errorDetails };
};

/**
 * Get all entity states
 * @returns {Promise<Array>} List of all entities with their states
 */
const getStates = async () => {
  try {
    const response = await homeAssistantApi.get('/api/states');
    return response.data;
  } catch (error) {
    throw handleError(error);
  }
};

/**
 * Get state for a specific entity
 * @param {string} entityId - The entity ID
 * @returns {Promise<Object>} Entity state
 */
const getState = async (entityId) => {
  try {
    const response = await homeAssistantApi.get(`/api/states/${entityId}`);
    return response.data;
  } catch (error) {
    throw handleError(error);
  }
};

/**
 * Call a Home Assistant service
 * @param {string} domain - The domain (e.g., 'light', 'switch')
 * @param {string} service - The service (e.g., 'turn_on', 'turn_off')
 * @param {Object} serviceData - The service data
 * @returns {Promise<Object>} Response from the service call
 */
const callService = async (domain, service, serviceData = {}) => {
  try {
    const response = await homeAssistantApi.post(
      `/api/services/${domain}/${service}`,
      serviceData
    );
    return response.data;
  } catch (error) {
    throw handleError(error);
  }
};

/**
 * Get Home Assistant configuration
 * @returns {Promise<Object>} Home Assistant configuration
 */
const getConfig = async () => {
  try {
    const response = await homeAssistantApi.get('/api/config');
    return response.data;
  } catch (error) {
    throw handleError(error);
  }
};

/**
 * Get history for entities
 * @param {Array} entityIds - Array of entity IDs
 * @param {string} startTime - Start time (ISO format)
 * @param {string} endTime - End time (ISO format)
 * @returns {Promise<Object>} Historical data for the entities
 */
const getHistory = async (entityIds = [], startTime = null, endTime = null) => {
  try {
    let url = '/api/history/period';
    
    // Add start time if provided
    if (startTime) {
      url += `/${startTime}`;
    }
    
    // Build query parameters
    const params = {};
    if (entityIds.length > 0) {
      params.filter_entity_id = entityIds.join(',');
    }
    if (endTime) {
      params.end_time = endTime;
    }
    
    const response = await homeAssistantApi.get(url, { params });
    return response.data;
  } catch (error) {
    throw handleError(error);
  }
};

/**
 * Get events from Home Assistant
 * @returns {Promise<Array>} List of available events
 */
const getEvents = async () => {
  try {
    const response = await homeAssistantApi.get('/api/events');
    return response.data;
  } catch (error) {
    throw handleError(error);
  }
};

export {
  homeAssistantApi,
  getStates,
  getState,
  callService,
  getConfig,
  getHistory,
  getEvents
};

