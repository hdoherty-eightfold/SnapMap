# Module 1: Frontend Core UI Agent

## Agent Identity
- **Agent Name**: Frontend Core UI Agent
- **Module ID**: MODULE_1
- **Role**: Frontend Lead - Upload, Preview, Export, UI Shell
- **Primary Developer**: Developer 1

## Responsibilities

### Core Components to Build
1. **FileUpload Component** ⭐
   - Drag-and-drop file upload interface
   - Supports CSV and Excel files (.csv, .xlsx, .xls)
   - Max file size: 100 MB
   - Upload progress indicator
   - File validation and error handling

2. **DataPreview Component** ⭐
   - Display uploaded data in table format
   - Show first 5-10 rows
   - Column headers with detected data types
   - Scrollable table for large datasets
   - Row and column count statistics

3. **ExportDownload Component** ⭐
   - Download transformed CSV
   - Success/error feedback
   - File naming conventions
   - UTF-8 encoding handling

4. **Layout Components**
   - App.tsx (main application shell)
   - Header, Footer, Navigation
   - ProgressStepper (shows current step in workflow)
   - Responsive layout structure

5. **Common UI Components**
   - Buttons (Primary, Secondary, Text, Icon)
   - Cards (Field card, Preview card, Summary card)
   - Modals
   - Toast notifications
   - Loading indicators
   - Error boundaries

### Services to Build
- **API Client** (services/api.ts)
  - Axios wrapper for all API calls
  - Error handling and retry logic
  - Request/response interceptors
  - CORS configuration

### Context to Provide
```typescript
// AppContext for sharing state across components
export interface AppContext {
  uploadedFile: FileData | null;
  schema: SchemaData | null;
  mappings: MappingConfig;
  transformedData: any[];
  validationResults: ValidationResult[];
  setMappings: (mappings: MappingConfig) => void;
  setUploadedFile: (file: FileData) => void;
  setSchema: (schema: SchemaData) => void;
}
```

## API Dependencies (Consume from Backend)

### POST /api/upload
**Purpose**: Upload and parse CSV/Excel file
**Request**: multipart/form-data with file
**Response**:
```typescript
interface UploadResponse {
  filename: string;
  row_count: number;
  column_count: number;
  columns: string[];
  sample_data: Record<string, any>[];
  data_types: Record<string, string>;
}
```

### GET /api/schema/employee
**Purpose**: Get Employee entity schema
**Response**:
```typescript
interface SchemaResponse {
  entity_name: string;
  fields: FieldDefinition[];
}
```

### POST /api/transform/export
**Purpose**: Export transformed CSV
**Request**:
```typescript
interface ExportRequest {
  mappings: MappingConfig;
  source_data: any[];
}
```
**Response**: CSV file download

## What You Provide to Other Modules

### To Module 2 (Mapping Engine)
- AppContext with shared state
- Common UI components (Button, Card, Modal, Toast)
- Layout structure

### Exports
```typescript
// Re-usable UI components
export { Button, Card, Modal, Toast, LoadingSpinner };

// Context
export { AppContext, AppContextProvider };

// Hooks
export { useAppContext };
```

## Tech Stack
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Icons**: lucide-react
- **HTTP Client**: Axios
- **State Management**: React Context + hooks

## File Structure
```
frontend/src/
├── App.tsx                    # Main app shell
├── main.tsx                   # Entry point
├── components/
│   ├── upload/
│   │   ├── FileUpload.tsx    ⭐ Priority 1
│   │   └── FileUpload.test.tsx
│   ├── preview/
│   │   ├── DataPreview.tsx   ⭐ Priority 2
│   │   └── DataTable.tsx
│   ├── export/
│   │   ├── ExportDownload.tsx ⭐ Priority 3
│   │   └── ExportButton.tsx
│   ├── common/
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Modal.tsx
│   │   ├── Toast.tsx
│   │   └── LoadingSpinner.tsx
│   └── layout/
│       ├── Layout.tsx
│       ├── Header.tsx
│       ├── Footer.tsx
│       └── ProgressStepper.tsx
├── contexts/
│   └── AppContext.tsx        ⭐ Priority 0 (First!)
├── services/
│   └── api.ts                ⭐ Priority 0 (First!)
├── hooks/
│   └── useAppContext.ts
├── types/
│   └── index.ts
└── utils/
    └── fileHelpers.ts
```

## Daily Deliverables

### Day 1 (8 hours)
- [x] Setup Vite + React + TypeScript project
- [x] Configure Tailwind CSS
- [x] Create AppContext
- [x] Create API client service
- [x] Build FileUpload component (functional)
- [x] Test API integration with mock data
- **Deliverable**: FileUpload component working with mocked API

### Day 2 (8 hours)
- [x] Build DataPreview component
- [x] Create Layout components (Header, Footer, ProgressStepper)
- [x] Build common UI components library
- [x] Implement responsive design
- **Deliverable**: Full UI shell with Upload → Preview flow

### Day 3 (6 hours)
- [x] Integration testing with real backend APIs
- [x] Handle error states
- [x] Implement loading states
- [x] Test CORS configuration
- **Deliverable**: Upload → Preview working with real backend

### Day 4 (6 hours)
- [x] Build ExportDownload component
- [x] Implement file download logic
- [x] Add success/error feedback
- [x] Test end-to-end flow
- **Deliverable**: Complete Upload → Preview → Export flow

### Day 5 (6 hours)
- [x] UI polish and refinements
- [x] Add animations and transitions
- [x] Improve error messages
- [x] Mobile responsiveness (if time permits)
- **Deliverable**: Polished, production-ready UI

### Day 6 (6 hours)
- [x] Bug fixes
- [x] Performance optimization
- [x] Accessibility improvements
- [x] User testing and feedback
- **Deliverable**: Stable, bug-free module

### Day 7 (6 hours)
- [x] Final integration testing
- [x] Demo preparation
- [x] Documentation
- **Deliverable**: Demo-ready application

## Mock Data for Independent Development

Use this while Module 3 & 4 build their APIs:

```typescript
// Mock upload response
export const MOCK_UPLOAD_RESPONSE: UploadResponse = {
  filename: "workday_export.csv",
  row_count: 150,
  column_count: 12,
  columns: [
    "EmpID", "FirstName", "LastName", "Email",
    "HireDate", "JobTitle", "Department", "Phone",
    "Location", "Manager", "Skill1", "Skill2"
  ],
  sample_data: [
    {
      EmpID: "E001",
      FirstName: "John",
      LastName: "Doe",
      Email: "john@company.com",
      HireDate: "10/30/2020",
      JobTitle: "Software Engineer",
      Department: "Engineering",
      Phone: "+1-555-0100",
      Location: "San Francisco",
      Manager: "Jane Smith",
      Skill1: "Python",
      Skill2: "JavaScript"
    },
    {
      EmpID: "E002",
      FirstName: "Jane",
      LastName: "Smith",
      Email: "jane@company.com",
      HireDate: "05/15/2019",
      JobTitle: "Senior Engineer",
      Department: "Engineering",
      Phone: "+1-555-0101",
      Location: "San Francisco",
      Manager: "Bob Johnson",
      Skill1: "Java",
      Skill2: "React"
    }
  ],
  data_types: {
    EmpID: "string",
    FirstName: "string",
    LastName: "string",
    Email: "email",
    HireDate: "date",
    JobTitle: "string",
    Department: "string",
    Phone: "string",
    Location: "string",
    Manager: "string",
    Skill1: "string",
    Skill2: "string"
  }
};

// Mock schema response
export const MOCK_SCHEMA: SchemaResponse = {
  entity_name: "employee",
  fields: [
    {
      name: "EMPLOYEE_ID",
      display_name: "Employee ID",
      type: "string",
      required: true,
      max_length: 50,
      example: "E001"
    },
    {
      name: "FIRST_NAME",
      display_name: "First Name",
      type: "string",
      required: true,
      max_length: 100,
      example: "John"
    },
    {
      name: "LAST_NAME",
      display_name: "Last Name",
      type: "string",
      required: true,
      max_length: 100,
      example: "Doe"
    },
    {
      name: "EMAIL",
      display_name: "Email Address",
      type: "email",
      required: true,
      pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
      example: "john@company.com"
    },
    {
      name: "HIRING_DATE",
      display_name: "Hiring Date",
      type: "date",
      required: false,
      format: "YYYY-MM-DD",
      example: "2020-10-30"
    }
  ]
};
```

## Integration Checkpoints

### Day 2 EOD
- ✅ Share AppContext interface with Module 2
- ✅ Share UI components library with Module 2
- ✅ Document component props and usage

### Day 3 EOD
- ✅ Test real API calls with Module 3 & 4
- ✅ Verify API contracts match implementation
- ✅ Handle CORS issues with Module 3

### Day 5 EOD
- ✅ Full integration test with all modules
- ✅ End-to-end flow testing
- ✅ Bug fixing session with team

## Success Criteria

### Functional Requirements
- ✅ File upload works with drag-and-drop
- ✅ Supports CSV and Excel files
- ✅ Preview displays uploaded data correctly
- ✅ Export downloads transformed CSV
- ✅ Error handling for all edge cases
- ✅ Loading states for all async operations

### Non-Functional Requirements
- ✅ Beautiful, professional UI design
- ✅ Smooth animations and transitions
- ✅ Fast load times (< 2 seconds)
- ✅ Responsive layout (works on different screen sizes)
- ✅ Accessible (keyboard navigation, screen readers)

### Code Quality
- ✅ TypeScript with strict mode
- ✅ Reusable, modular components
- ✅ Proper error boundaries
- ✅ Clean, readable code
- ✅ Comments for complex logic

## Common Pitfalls to Avoid
1. ❌ Don't build everything yourself - use existing libraries
2. ❌ Don't skip error handling - users will encounter errors
3. ❌ Don't ignore loading states - async operations take time
4. ❌ Don't hardcode values - use constants and configuration
5. ❌ Don't skip TypeScript types - they catch bugs early

## Resources
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Vite Guide](https://vitejs.dev/guide/)
- [Lucide Icons](https://lucide.dev/)

## Questions or Blockers?
- **Module 2 (Mapping)**: For AppContext or component integration
- **Module 3 (Transform)**: For API issues or data format questions
- **Module 4 (Schema)**: For schema format or field definitions
- **Team Chat**: For quick questions or help requests
- **Daily Standup**: For status updates and coordination

---

**Remember**: You are building the foundation that everyone else depends on. Focus on:
1. **Stability**: No crashes, good error handling
2. **Clarity**: Clean, well-documented code
3. **Beauty**: First impressions matter for the demo
4. **Speed**: Fast load times and responsive UI

You've got this! 🚀
