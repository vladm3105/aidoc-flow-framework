/**
 * n8n Custom Node Examples
 *
 * Demonstrates custom node development patterns:
 * - Programmatic style (full control)
 * - Declarative style (simplified)
 */

import {
  INodeType,
  INodeTypeDescription,
  IExecuteFunctions,
  INodeProperties,
  IRouter
} from 'n8n-workflow';


// =============================================================================
// Example 1: Programmatic Style Custom Node (Full Control)
// =============================================================================

/**
 * Use for:
 * - Complex authentication flows
 * - Advanced parameter validation
 * - Custom UI components
 * - Polling operations with state management
 *
 * Complexity: 3-4
 */
export class CustomNode implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'Custom Node',
    name: 'customNode',
    group: ['transform'],
    version: 1,
    description: 'Custom functionality',
    defaults: {
      name: 'Custom Node',
    },
    inputs: ['main'],
    outputs: ['main'],
    credentials: [
      {
        name: 'customApi',
        required: true,
      },
    ],
    properties: [
      {
        displayName: 'Operation',
        name: 'operation',
        type: 'options',
        options: [
          {
            name: 'Get',
            value: 'get',
          },
          {
            name: 'Create',
            value: 'create',
          },
        ],
        default: 'get',
      },
    ],
  };

  async execute(this: IExecuteFunctions) {
    const items = this.getInputData();
    const returnData = [];

    for (let i = 0; i < items.length; i++) {
      const operation = this.getNodeParameter('operation', i);
      const credentials = await this.getCredentials('customApi');

      // Implementation logic
      const result = await this.helpers.request({
        method: 'GET',
        url: `https://api.example.com/${operation}`,
        headers: {
          'Authorization': `Bearer ${credentials.apiKey}`,
        },
      });

      returnData.push({ json: result });
    }

    return [returnData];
  }
}


// =============================================================================
// Example 2: Declarative Style Custom Node (Simplified)
// =============================================================================

/**
 * Use for:
 * - Standard CRUD operations
 * - RESTful API wrappers
 * - Simple integrations without complex logic
 *
 * Complexity: 2
 */

// Define node properties
export const operations: INodeProperties[] = [
  {
    displayName: 'Resource',
    name: 'resource',
    type: 'options',
    options: [
      { name: 'User', value: 'user' },
      { name: 'Project', value: 'project' },
    ],
    default: 'user',
  },
];

// Routing defined declaratively
export const router: IRouter = {
  user: {
    get: {
      routing: {
        request: {
          method: 'GET',
          url: '=/users/{{$parameter.userId}}',
        },
      },
    },
    create: {
      routing: {
        request: {
          method: 'POST',
          url: '/users',
          body: {
            name: '={{$parameter.name}}',
            email: '={{$parameter.email}}',
          },
        },
      },
    },
  },
  project: {
    get: {
      routing: {
        request: {
          method: 'GET',
          url: '=/projects/{{$parameter.projectId}}',
        },
      },
    },
    list: {
      routing: {
        request: {
          method: 'GET',
          url: '/projects',
        },
      },
    },
  },
};


// =============================================================================
// Example 3: Custom Credential Configuration
// =============================================================================

/**
 * Credential definition for API key authentication
 */
export const customApiCredentials = {
  displayName: 'Custom API Credentials',
  name: 'customApi',
  type: 'credentials',
  properties: [
    {
      displayName: 'API Key',
      name: 'apiKey',
      type: 'string',
      typeOptions: {
        password: true,
      },
      default: '',
      required: true,
    },
    {
      displayName: 'API URL',
      name: 'apiUrl',
      type: 'string',
      default: 'https://api.example.com',
      required: true,
    },
  ],
};


// =============================================================================
// Example 4: Credential Validation
// =============================================================================

/**
 * Test credential validity by making API request
 */
export async function validateCredentials(
  credentials: any,
  helpers: any
): Promise<boolean> {
  try {
    const response = await helpers.request({
      method: 'GET',
      url: `${credentials.apiUrl}/validate`,
      headers: {
        'Authorization': `Bearer ${credentials.apiKey}`,
      },
    });
    return response.valid === true;
  } catch (error) {
    return false;
  }
}


// =============================================================================
// Example 5: Polling Trigger Node (Advanced)
// =============================================================================

/**
 * Poll external API for new records
 * Complexity: 4-5
 */
export class PollingTrigger implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'Polling Trigger',
    name: 'pollingTrigger',
    group: ['trigger'],
    version: 1,
    description: 'Polls API for new data',
    defaults: {
      name: 'Polling Trigger',
    },
    inputs: [],
    outputs: ['main'],
    credentials: [
      {
        name: 'customApi',
        required: true,
      },
    ],
    polling: true,
    properties: [
      {
        displayName: 'Polling Interval',
        name: 'pollInterval',
        type: 'number',
        default: 60,
        description: 'Seconds between polls',
      },
    ],
  };

  async poll(this: IExecuteFunctions) {
    const credentials = await this.getCredentials('customApi');
    const pollInterval = this.getNodeParameter('pollInterval', 0) as number;

    // Get last poll time from state
    const state = this.getWorkflowStaticData('node');
    const lastPoll = state.lastPoll || 0;

    // Fetch new records since lastPoll
    const response = await this.helpers.request({
      method: 'GET',
      url: `${credentials.apiUrl}/records?since=${lastPoll}`,
      headers: {
        'Authorization': `Bearer ${credentials.apiKey}`,
      },
      json: true,
    });

    // Update state
    state.lastPoll = Date.now();

    // Return new records
    if (response.data && response.data.length > 0) {
      return [response.data.map((item: any) => ({ json: item }))];
    }

    return null; // No new data
  }
}


// =============================================================================
// Development Workflow Commands
// =============================================================================

/**
 * Command Reference:
 *
 * # Create from template
 * npm create @n8n/node my-custom-node
 *
 * # Build TypeScript
 * npm run build
 *
 * # Link locally for testing
 * npm link
 *
 * # In n8n development environment
 * cd ~/.n8n/nodes
 * npm link my-custom-node
 *
 * # Restart n8n to load node
 * n8n start
 *
 * # Publish to npm (community node)
 * npm publish
 *
 * # Install in n8n
 * Settings → Community Nodes → Install → Enter package name
 */
