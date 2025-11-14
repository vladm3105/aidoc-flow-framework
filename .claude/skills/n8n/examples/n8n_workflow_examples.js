/**
 * n8n Workflow Code Node Examples
 *
 * JavaScript code patterns for n8n Code nodes:
 * - Data transformation
 * - API calls
 * - Error handling
 * - Pagination
 * - Webhook responses
 */


// =============================================================================
// Example 1: Basic Data Transformation
// =============================================================================

/**
 * Process input items and transform data
 * Complexity: 1
 */
function basicTransformation() {
  // Access input items
  const items = $input.all();

  // Process data
  const processedItems = items.map(item => {
    const inputData = item.json;

    return {
      json: {
        // Output fields
        processed: inputData.field.toUpperCase(),
        timestamp: new Date().toISOString()
      }
    };
  });

  // Return transformed items
  return processedItems;
}


// =============================================================================
// Example 2: Filtering Data
// =============================================================================

/**
 * Filter items based on conditions
 * Complexity: 1
 */
function filterData() {
  const items = $input.all();
  return items.filter(item => item.json.status === 'active');
}


// =============================================================================
// Example 3: Aggregation with Lodash
// =============================================================================

/**
 * Group and aggregate data
 * Complexity: 2
 */
function aggregateData() {
  const items = $input.all();
  const grouped = _.groupBy(items, item => item.json.category);

  return [{
    json: {
      summary: Object.keys(grouped).map(category => ({
        category,
        count: grouped[category].length
      }))
    }
  }];
}


// =============================================================================
// Example 4: Async API Calls
// =============================================================================

/**
 * Fetch data from external API for each item
 * Complexity: 2
 */
async function enrichWithAPI() {
  const items = $input.all();
  const results = [];

  for (const item of items) {
    const response = await fetch(`https://api.example.com/data/${item.json.id}`);
    const data = await response.json();

    results.push({
      json: {
        original: item.json,
        enriched: data
      }
    });
  }

  return results;
}


// =============================================================================
// Example 5: Error Handling in Transformations
// =============================================================================

/**
 * Handle errors gracefully during processing
 * Complexity: 2
 */
function transformWithErrorHandling() {
  const items = $input.all();

  return items.map(item => {
    try {
      // Risky operation
      const result = JSON.parse(item.json.data);
      return { json: { parsed: result } };
    } catch (error) {
      return {
        json: {
          error: error.message,
          original: item.json.data
        }
      };
    }
  });
}


// =============================================================================
// Example 6: API Pagination Handler
// =============================================================================

/**
 * Handle paginated API responses
 * Complexity: 3
 */
async function handlePagination() {
  let allResults = [];
  let page = 1;
  let hasMore = true;

  while (hasMore) {
    const response = await this.helpers.request({
      method: 'GET',
      url: `https://api.example.com/data?page=${page}`,
      json: true,
    });

    allResults = allResults.concat(response.results);
    hasMore = response.hasNext;
    page++;
  }

  return allResults.map(item => ({ json: item }));
}


// =============================================================================
// Example 7: Webhook Response Handler
// =============================================================================

/**
 * Process webhook data and return synchronous response
 * Complexity: 2
 */
function processWebhook() {
  // In Code node after webhook trigger
  const webhookData = $input.first().json;

  // Process data
  const result = {
    processed: webhookData.value * 2,
    timestamp: new Date().toISOString()
  };

  // Return response (synchronous webhook)
  return [{
    json: {
      status: 'success',
      data: result
    }
  }];
}


// =============================================================================
// Example 8: Batch Processing for Database
// =============================================================================

/**
 * Prepare data for batch database insert
 * Complexity: 2
 */
function prepareBatchInsert() {
  const items = $input.all();
  const values = items.map(item => ({
    name: item.json.name,
    email: item.json.email,
    created_at: new Date().toISOString()
  }));

  return [{ json: { values } }];

  // Next node: PostgreSQL
  // INSERT INTO users (name, email, created_at)
  // VALUES {{ $json.values }}
}


// =============================================================================
// Example 9: Data Validation
// =============================================================================

/**
 * Validate input data structure
 * Complexity: 2
 */
function validateInputData() {
  const items = $input.all();

  for (const item of items) {
    if (!item.json.email || !item.json.name) {
      throw new Error(`Invalid input: missing required fields at item ${item.json.id}`);
    }
  }

  return items;
}


// =============================================================================
// Example 10: API Call with Error Context
// =============================================================================

/**
 * Make API calls with detailed error reporting
 * Complexity: 3
 */
async function apiCallWithContext() {
  const items = $input.all();
  const results = [];

  for (const item of items) {
    try {
      const result = await fetch(`https://api.example.com/data/${item.json.id}`);
      const data = await result.json();
      results.push({ json: data });
    } catch (error) {
      throw new Error(`API call failed for ID ${item.json.id}: ${error.message}`);
    }
  }

  return results;
}


// =============================================================================
// Example 11: Idempotency Check
// =============================================================================

/**
 * Check existence before creation (idempotent operations)
 * Complexity: 2
 */
async function checkBeforeCreate() {
  const items = $input.all();
  const results = [];

  for (const item of items) {
    // Check if record exists
    const exists = await checkExists(item.json.uniqueId);

    if (!exists) {
      const created = await createRecord(item.json);
      results.push({ json: created });
    } else {
      results.push({ json: { skipped: true, id: item.json.uniqueId } });
    }
  }

  return results;
}

async function checkExists(id) {
  // Implementation would check database/API
  return false;
}

async function createRecord(data) {
  // Implementation would create record
  return { ...data, id: Math.random() };
}


// =============================================================================
// Example 12: AI Agent State Management
// =============================================================================

/**
 * Initialize and update state for iterative AI agent
 * Complexity: 3
 */

// Initialize state
function initializeAgentState() {
  return [{
    json: {
      task: 'Research topic',
      iteration: 0,
      maxIterations: 5,
      context: [],
      completed: false
    }
  }];
}

// Update state after agent action
function updateAgentState() {
  const state = $json;
  state.iteration++;
  state.context.push($('AI Agent').item.json.response);
  state.completed = state.iteration >= state.maxIterations || checkGoalMet(state);

  return [{ json: state }];
}

function checkGoalMet(state) {
  // Check if agent achieved goal
  return state.context.some(item => item.includes('completed'));
}


// =============================================================================
// Example 13: Debug Logging
// =============================================================================

/**
 * Add debug logging for troubleshooting
 * Complexity: 1
 */
function debugLogging() {
  const data = $json;
  console.log('Debug data:', JSON.stringify(data, null, 2));
  return [{ json: data }];
}


// =============================================================================
// Data Access Pattern Examples
// =============================================================================

/**
 * Common n8n expression patterns
 */

// Current node output
// {{ $json.field }}

// Specific node output
// {{ $('NodeName').item.json.field }}

// All items from input
// {{ $input.all() }}

// First item only
// {{ $input.first() }}

// Current item index
// {{ $itemIndex }}

// Previous node binary data
// {{ $binary.data }}

// Environment variable
// {{ $env.VARIABLE_NAME }}


// =============================================================================
// Available Libraries in n8n Code Nodes
// =============================================================================

/**
 * JavaScript Code Node:
 * - Node.js built-ins: fs, path, crypto, https
 * - Lodash: _.groupBy(), _.sortBy(), _.uniq(), etc.
 * - Luxon: DateTime manipulation
 * - n8n helpers: $input, $json, $binary, this.helpers
 *
 * Python Code Node:
 * - Standard library: json, datetime, re, requests
 * - NumPy: Array operations
 * - Pandas: Data analysis (if installed)
 * - _input: Access to input items
 */
