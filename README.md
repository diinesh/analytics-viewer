# Analytics Viewer

A natural language analytics platform that converts plain English queries into ClickHouse SQL and renders interactive dashboards. Built with React (TypeScript) frontend and FastAPI backend, powered by OpenAI for intelligent query conversion.

## Features

- 🗣️ **Natural Language Queries**: Ask questions about your data in plain English
- 🤖 **AI-Powered SQL Generation**: Automatically converts natural language to ClickHouse SQL using OpenAI
- 📊 **Multiple Visualization Types**: Bar charts, line charts, pie charts, scatter plots, and data tables
- 📋 **Interactive SQL Display**: View and copy the generated SQL queries
- ⚡ **Real-time Processing**: Live query execution with loading states
- 🎯 **Smart Chart Detection**: Automatically selects the best visualization based on query context and data

## Architecture

```
├── frontend/          # React TypeScript application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API service layer
│   │   ├── types/         # TypeScript interfaces
│   │   └── App.tsx        # Main application
└── backend/           # FastAPI Python application
    ├── main.py            # FastAPI server with ClickHouse integration
    ├── requirements.txt   # Python dependencies
    └── .env.example       # Environment variables template
```

## Prerequisites

- Node.js (v14 or higher)
- Python 3.9+
- ClickHouse database
- OpenAI API key

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd analytics-viewer
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

Edit `.env` file with your credentials:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# ClickHouse Cloud Configuration
CLICKHOUSE_HOST=your_clickhouse_cloud_host.clickhouse.cloud
CLICKHOUSE_PORT=8443
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=your_clickhouse_password
CLICKHOUSE_DATABASE=your_database_name
CLICKHOUSE_SECURE=true
```

**Note**: This project is configured to work with ClickHouse Cloud. For local ClickHouse installations, set `CLICKHOUSE_SECURE=false` and use port 8123.

### 3. Database Schema

This project is designed for comprehensive trend analysis across multiple data sources with the following main tables:

**Content Analysis:**
- **`zero_shot_analysis`**: Main analysis results with topics, confidence scores, and metadata
- **`zero_shot_entities`**: Named entities extracted from analyzed content  
- **`zero_shot_trends`**: Trend analysis and momentum tracking
- **`content_sources`**: Content source tracking and crawling statistics

**Social Media & Search Trends:**
- **`google_trends`**: Google Trends data for trending topics and keyword search volumes
- **`google_trends_related`**: Related queries from Google Trends
- **`x_trending_topics`**: X.com (Twitter) trending topics with virality and marketing analysis

**Aggregated Views:**
- **`daily_analysis_stats`**: Daily aggregations of zero-shot analysis
- **`cross_source_topic_correlation`**: Cross-platform topic correlations
- **`daily_trending_insights`**: Combined trending insights across all sources

The schema is optimized for time-series analysis, cross-platform correlation, and marketing intelligence. See `backend/sql/clickhouse/clickhouse_schema.sql` for the complete schema definition.

### 4. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install
```

## Usage

### 1. Start the Backend Server

```bash
cd backend
source venv/bin/activate
python main.py
```

The API server will start on `http://localhost:8000`

### 2. Start the Frontend Application

```bash
cd frontend
npm start
```

The React application will start on `http://localhost:3000`

### 3. Query Your Data

Open your browser and navigate to `http://localhost:3000`. You can now ask questions about your data in natural language:

**Example Queries for Multi-Source Trend Analysis:**

*Content Analysis:*
- "Show me the top topics analyzed over the last 7 days"
- "What are the confidence scores distribution by broad category?"
- "Display trending topics with high marketing intent"
- "Show me entity mentions by type over time"

*Social Media & Search Trends:*
- "What are the most viral topics on X.com with high marketing potential?"
- "Show me Google Trends data for topics with rising interest"
- "Which X.com trending topics have the best brand safety scores?"
- "Display search volume trends by geographic location"

*Cross-Platform Analysis:*
- "Compare topics trending across Google Trends and X.com"
- "Show me correlations between content analysis and social media trends"
- "Which topics are trending on multiple platforms simultaneously?"
- "Display marketing opportunities across all data sources"

*Business Intelligence:*
- "What are the demographics for trending marketing opportunities?"
- "Show me trend momentum across different business contexts"
- "Which content sources have the highest success rates?"

## API Endpoints

### `POST /api/query`

Processes natural language queries and returns SQL results with visualization recommendations.

**Request:**
```json
{
  "query": "Show me sales by region"
}
```

**Response:**
```json
{
  "sql": "SELECT region, SUM(sales) FROM sales_table GROUP BY region",
  "data": [
    {"region": "North", "sales": 150000},
    {"region": "South", "sales": 120000}
  ],
  "chart_type": "bar",
  "title": "Results: Show me sales by region"
}
```

### `GET /api/health`

Health check endpoint that returns server status and ClickHouse connection status.

## Configuration

### ClickHouse Setup

Ensure your ClickHouse database is running and accessible. The application will automatically discover your database schema and use it for query generation.

### OpenAI Configuration

The application uses OpenAI's GPT-3.5-turbo model for natural language to SQL conversion. Make sure you have:
1. A valid OpenAI API key
2. Sufficient API credits
3. Proper rate limits configured

## Chart Type Detection

The system automatically selects visualization types based on:

- **Line Charts**: Time series data, trends, temporal patterns
- **Bar Charts**: Comparisons, categorical data, grouped metrics
- **Pie Charts**: Distribution, breakdown, percentage analysis
- **Scatter Plots**: Correlation between two numeric variables
- **Data Tables**: Complex data, multiple columns, detailed views

## Development

### Frontend Development

```bash
cd frontend
npm start          # Start development server
npm test           # Run tests
npm run build      # Create production build
```

### Backend Development

```bash
cd backend
source venv/bin/activate
python main.py     # Start development server
```

## Troubleshooting

### Common Issues

1. **ClickHouse Connection Failed**
   - Verify ClickHouse is running
   - Check connection credentials in `.env`
   - Ensure network connectivity

2. **OpenAI API Errors**
   - Verify API key is valid
   - Check API usage limits
   - Ensure sufficient credits

3. **Frontend Build Errors**
   - Delete `node_modules` and run `npm install`
   - Check Node.js version compatibility

### Logs

Backend logs are displayed in the terminal. Frontend logs are available in browser developer console.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For questions or issues, please create an issue in the repository or contact the development team.