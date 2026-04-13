/**
 * User Data API Interface (SQL.js)
 * Manages profile information, product listings, news, and JSON/XML data over HTTP.
 * Can be configured to use mock data, local storage, or actual HTTP endpoints.
 */

class UserDataAPI {
    constructor(config = {}) {
        this.useMock = config.useMock !== undefined ? config.useMock : true;
        this.baseUrl = config.baseUrl || 'http://localhost:3000/api/v1';
        this.delayMs = config.delayMs || 500;
        
        // Initialize mock databases if using mock mode
        if (this.useMock) {
            this._initMockData();
        }
    }

    /**
     * Helper to simulate network latency
     */
    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Initialize mock storage for local testing
     */
    _initMockData() {
        if (!localStorage.getItem('mock_db_profile')) {
            localStorage.setItem('mock_db_profile', JSON.stringify({
                name: 'Guest User',
                bio: 'Welcome to your profile!',
                avatar: 'developer.png',
                joined: new Date().toISOString()
            }));
        }
        if (!localStorage.getItem('mock_db_products')) {
            localStorage.setItem('mock_db_products', JSON.stringify([
                { id: 1, name: 'Premium Component Library', price: 49.99, category: 'Software Development' },
                { id: 2, name: 'Advanced UI Kit', price: 29.99, category: 'Design Tools' }
            ]));
        }
        if (!localStorage.getItem('mock_db_news')) {
            localStorage.setItem('mock_db_news', JSON.stringify([
                { id: 1, title: 'Platform Update 2.0 Released', date: new Date().toISOString().split('T')[0], content: 'We have updated our core features with massive performance improvements.' }
            ]));
        }
    }

    // ==========================================
    // Profile Information Management
    // ==========================================

    async getProfile() {
        if (!this.useMock) {
            const response = await fetch(`${this.baseUrl}/profile`);
            if (!response.ok) throw new Error(await response.text());
            return await response.json();
        }
        
        await this._sleep(this.delayMs);
        return JSON.parse(localStorage.getItem('mock_db_profile'));
    }

    async updateProfile(data) {
        if (!this.useMock) {
            const response = await fetch(`${this.baseUrl}/profile`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error(await response.text());
            return await response.json();
        }
        
        await this._sleep(this.delayMs);
        const currentData = JSON.parse(localStorage.getItem('mock_db_profile'));
        const updatedData = { ...currentData, ...data };
        localStorage.setItem('mock_db_profile', JSON.stringify(updatedData));
        return { success: true, message: 'Profile updated successfully', profile: updatedData };
    }

    // ==========================================
    // Product Listings Management
    // ==========================================

    async getProducts() {
        if (!this.useMock) {
            const response = await fetch(`${this.baseUrl}/products`);
            if (!response.ok) throw new Error(await response.text());
            return await response.json();
        }
        
        await this._sleep(this.delayMs);
        return JSON.parse(localStorage.getItem('mock_db_products'));
    }

    async addProduct(product) {
        if (!this.useMock) {
            const response = await fetch(`${this.baseUrl}/products`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(product)
            });
            if (!response.ok) throw new Error(await response.text());
            return await response.json();
        }
        
        await this._sleep(this.delayMs);
        const products = JSON.parse(localStorage.getItem('mock_db_products'));
        const newProduct = { id: Date.now(), ...product };
        products.push(newProduct);
        localStorage.setItem('mock_db_products', JSON.stringify(products));
        return { success: true, message: 'Product added successfully', product: newProduct };
    }

    // ==========================================
    // News Management
    // ==========================================

    async getNews() {
        if (!this.useMock) {
            const response = await fetch(`${this.baseUrl}/news`);
            if (!response.ok) throw new Error(await response.text());
            return await response.json();
        }
        
        await this._sleep(this.delayMs);
        return JSON.parse(localStorage.getItem('mock_db_news'));
    }

    async addNewsItem(newsItem) {
        if (!this.useMock) {
            const response = await fetch(`${this.baseUrl}/news`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newsItem)
            });
            if (!response.ok) throw new Error(await response.text());
            return await response.json();
        }
        
        await this._sleep(this.delayMs);
        const news = JSON.parse(localStorage.getItem('mock_db_news'));
        const newEntry = { id: Date.now(), date: new Date().toISOString().split('T')[0], ...newsItem };
        news.push(newEntry);
        localStorage.setItem('mock_db_news', JSON.stringify(news));
        return { success: true, message: 'News added successfully', news: newEntry };
    }

    // ==========================================
    // JSON / XML Data HTTP Request Handlers
    // ==========================================

    /**
     * Fetch external or internal JSON data over HTTP
     * @param {string} url - API Endpoint
     * @param {Object} options - Fetch options
     * @returns {Promise<Object>} JSON response
     */
    async fetchJsonData(url, options = {}) {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Accept': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error while fetching JSON! Status: ${response.status}`);
        }
        return await response.json();
    }

    /**
     * Fetch external or internal XML data over HTTP
     * @param {string} url - API Endpoint
     * @param {Object} options - Fetch options
     * @param {boolean} parseToDOM - Whether to parse XML string into a DOM element
     * @returns {Promise<Document | string>} XML Document or raw string
     */
    async fetchXmlData(url, options = {}, parseToDOM = true) {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Accept': 'application/xml, text/xml',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error while fetching XML! Status: ${response.status}`);
        }
        
        const xmlText = await response.text();
        
        if (parseToDOM) {
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(xmlText, "text/xml");
            
            // Basic error handling for XML parser
            const parserError = xmlDoc.getElementsByTagName("parsererror");
            if (parserError.length > 0) {
                throw new Error("Error parsing XML: " + parserError[0].textContent);
            }
            return xmlDoc;
        }
        
        return xmlText;
    }
}

// Instantiate globally to be accessible by frontend scripts
const userDataAPI = new UserDataAPI({ useMock: true });
