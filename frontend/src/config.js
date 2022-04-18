const config = {
    apiBasePath: process.env.REACT_APP_API_BASE_PATH || 'http://localhost:8000/api',
    reactAppMode: process.env.REACT_APP_MODE || 'dev',
}

export default config;