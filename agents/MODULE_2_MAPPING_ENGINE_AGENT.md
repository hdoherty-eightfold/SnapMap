# Module 2: Field Mapping Engine Agent

## Agent Identity
- **Agent Name**: Field Mapping Engine Agent
- **Module ID**: MODULE_2
- **Role**: Frontend Specialist - Drag & Drop, Visual Lines, Auto-Map UI
- **Primary Developer**: Developer 2

## Responsibilities

### Core Components to Build
1. **FieldMapping Component** ⭐⭐ (Main Component)
   - Two-column layout (Source fields | Target fields)
   - Progress indicator (% of required fields mapped)
   - Auto-Map button integration
   - Mapping state management
   - Visual feedback for user interactions

2. **Drag-and-Drop System** ⭐⭐
   - DraggableField component (source fields)
   - DroppableField component (target fields)
   - Drag feedback (cursor changes, hover effects)
   - Drop validation
   - Undo mapping functionality

3. **ConnectionLines Component** ⭐⭐ (Visual Lines)
   - SVG overlay between columns
   - Animated connection lines
   - Color-coded by confidence:
     - 🟢 Green (100% - exact match)
     - 🟡 Yellow (90-99% - fuzzy match)
     - ⚪ Gray (manual mapping)
   - Smooth Bézier curves
   - Hover interactions

4. **Auto-Map Button & Logic**
   - Prominent UI placement
   - Animated feedback when clicked
   - Shows toast: "X fields mapped automatically!"
   - Integrates with auto-map API

5. **ValidationPanel Component**
   - Shows validation errors/warnings
   - Color-coded messages (Error, Warning, Info)
   - Clickable to jump to field
   - Counts display

6. **Field Lists**
   - SourceFieldList (customer's fields)
   - TargetFieldList (Eightfold's fields)
   - Required field indicators
   - Sample data display
   - Data type indicators

### Hooks to Build
```typescript
// useDragDrop.ts - Drag-and-drop logic
export const useDragDrop = () => {
  // Returns drag/drop handlers
};

// useMapping.ts - Mapping state management
export const useMapping = () => {
  // Returns mappings state and setters
};

// useAutoMap.ts - Auto-map integration
export const useAutoMap = () => {
  // Returns auto-map trigger function
};
```

### Utils to Build
```typescript
// lineCalculations.ts - SVG coordinate calculations
export const calculateLineCoordinates = (
  sourceElement: HTMLElement,
  targetElement: HTMLElement
) => {
  // Returns SVG path for Bézier curve
};
```

## API Dependencies (Consume from Backend)

### POST /api/auto-map
**Purpose**: Automatically match source fields to target fields
**Request**:
```typescript
interface AutoMapRequest {
  source_fields: string[];
  target_schema: FieldDefinition[];
}
```
**Response**:
```typescript
interface AutoMapResponse {
  mappings: Mapping[];
  total_mapped: number;
  total_source: number;
  mapping_percentage: number;
}

interface Mapping {
  source: string;
  target: string;
  confidence: number;  // 0.0 to 1.0
  method: 'exact' | 'fuzzy' | 'alias';
}
```

### POST /api/transform/preview
**Purpose**: Preview transformation with current mappings
**Request**:
```typescript
interface PreviewRequest {
  mappings: MappingConfig;
  source_data: any[];
  sample_size: number;
}
```
**Response**:
```typescript
interface PreviewResponse {
  transformed_data: any[];
  transformations_applied: string[];
}
```

### POST /api/validate
**Purpose**: Validate current mappings
**Request**:
```typescript
interface ValidationRequest {
  mappings: MappingConfig;
  source_data: any[];
}
```
**Response**:
```typescript
interface ValidationResponse {
  errors: ValidationError[];
  warnings: ValidationWarning[];
  is_valid: boolean;
}
```

## What You Provide to Other Modules

### To Module 1 (Frontend Core)
- MappingConfig data structure
- Mapping component integration

### Exports
```typescript
// Main component
export { FieldMapping };

// Mapping configuration format
export interface MappingConfig {
  mappings: Array<{
    source: string;
    target: string;
    confidence: number;
    method: 'exact' | 'fuzzy' | 'manual';
  }>;
  validations: ValidationResult[];
}

// Hook for other components
export { useMapping };
```

## Tech Stack
- **Framework**: React 18 + TypeScript
- **Drag & Drop**: @dnd-kit/core (or react-dnd)
- **Styling**: Tailwind CSS
- **SVG**: Native SVG elements
- **Animations**: CSS transitions + Framer Motion (optional)
- **Icons**: lucide-react

## File Structure
```
frontend/src/
├── components/
│   └── mapping/
│       ├── FieldMapping.tsx           ⭐ Priority 1 (Main)
│       ├── SourceFieldList.tsx        ⭐ Priority 2
│       ├── TargetFieldList.tsx        ⭐ Priority 2
│       ├── DraggableField.tsx         ⭐ Priority 3
│       ├── DroppableField.tsx         ⭐ Priority 3
│       ├── ConnectionLines.tsx        ⭐ Priority 4
│       ├── AutoMapButton.tsx          ⭐ Priority 5
│       ├── ValidationPanel.tsx
│       ├── MappingProgress.tsx
│       └── FieldCard.tsx
├── hooks/
│   ├── useDragDrop.ts                 ⭐ Priority 1
│   ├── useMapping.ts                  ⭐ Priority 1
│   └── useAutoMap.ts
└── utils/
    ├── lineCalculations.ts            ⭐ Priority 4
    └── mappingHelpers.ts
```

## Daily Deliverables

### Day 1 (8 hours)
- [x] Setup @dnd-kit/core or react-dnd
- [x] Create useDragDrop hook
- [x] Create useMapping hook
- [x] Build basic FieldMapping shell component
- [x] Test drag-and-drop with simple example
- **Deliverable**: Basic drag-and-drop working

### Day 2 (8 hours)
- [x] Build SourceFieldList component ⭐
- [x] Build TargetFieldList component ⭐
- [x] Build DraggableField component
- [x] Build DroppableField component
- [x] Implement mapping state management
- [x] Add visual feedback (hover, active states)
- **Deliverable**: Full drag-and-drop field mapping

### Day 3 (6 hours)
- [x] Build ConnectionLines component ⭐
- [x] Implement SVG line drawing
- [x] Calculate line coordinates
- [x] Add color-coding by confidence
- [x] Test line updates on remapping
- **Deliverable**: Visual connection lines working

### Day 4 (6 hours)
- [x] Build AutoMapButton component
- [x] Integrate with auto-map API
- [x] Add animated feedback
- [x] Test auto-mapping accuracy
- [x] Handle edge cases
- **Deliverable**: Auto-map feature working

### Day 5 (6 hours)
- [x] Build ValidationPanel component
- [x] Integrate with validation API
- [x] Add error/warning/info messages
- [x] Implement click-to-jump functionality
- [x] Add MappingProgress indicator
- **Deliverable**: Complete validation UI

### Day 6 (6 hours)
- [x] Polish animations and transitions
- [x] Improve hover interactions
- [x] Handle edge cases (unmapping, remapping)
- [x] Performance optimization
- [x] User testing feedback
- **Deliverable**: Polished, production-ready mapping

### Day 7 (6 hours)
- [x] Final integration testing
- [x] Bug fixes
- [x] Demo preparation
- **Deliverable**: Demo-ready mapping interface

## Mock Data for Independent Development

Use this while Module 4 builds auto-map API:

```typescript
// Mock auto-map response
export const MOCK_AUTO_MAP_RESPONSE: AutoMapResponse = {
  mappings: [
    {
      source: "EmpID",
      target: "EMPLOYEE_ID",
      confidence: 1.0,
      method: "exact"
    },
    {
      source: "FirstName",
      target: "FIRST_NAME",
      confidence: 0.95,
      method: "fuzzy"
    },
    {
      source: "LastName",
      target: "LAST_NAME",
      confidence: 0.95,
      method: "fuzzy"
    },
    {
      source: "Email",
      target: "EMAIL",
      confidence: 1.0,
      method: "exact"
    },
    {
      source: "HireDate",
      target: "HIRING_DATE",
      confidence: 0.90,
      method: "fuzzy"
    },
    {
      source: "JobTitle",
      target: "TITLE",
      confidence: 0.85,
      method: "fuzzy"
    },
    {
      source: "Department",
      target: "BUSINESS_UNIT",
      confidence: 0.80,
      method: "alias"
    },
    {
      source: "Phone",
      target: "PHONE",
      confidence: 1.0,
      method: "exact"
    }
  ],
  total_mapped: 8,
  total_source: 12,
  mapping_percentage: 67
};

// Mock validation response
export const MOCK_VALIDATION_RESPONSE: ValidationResponse = {
  errors: [],
  warnings: [
    {
      field: "TITLE",
      message: "Optional field not mapped",
      severity: "warning"
    },
    {
      field: "LAST_ACTIVITY_TS",
      message: "Required field not mapped",
      severity: "error"
    }
  ],
  is_valid: false
};
```

## Drag-and-Drop Implementation Guide

### Using @dnd-kit/core (Recommended)

```typescript
// DraggableField.tsx
import { useDraggable } from '@dnd-kit/core';

export const DraggableField: React.FC<Props> = ({ field }) => {
  const { attributes, listeners, setNodeRef, transform } = useDraggable({
    id: field.name,
    data: field
  });

  const style = {
    transform: transform ? `translate3d(${transform.x}px, ${transform.y}px, 0)` : undefined,
  };

  return (
    <div ref={setNodeRef} style={style} {...listeners} {...attributes}>
      {/* Field card UI */}
    </div>
  );
};

// DroppableField.tsx
import { useDroppable } from '@dnd-kit/core';

export const DroppableField: React.FC<Props> = ({ field }) => {
  const { isOver, setNodeRef } = useDroppable({
    id: field.name,
    data: field
  });

  return (
    <div
      ref={setNodeRef}
      className={isOver ? 'border-blue-500' : 'border-gray-300'}
    >
      {/* Field card UI */}
    </div>
  );
};
```

## SVG Connection Lines Implementation

```typescript
// ConnectionLines.tsx
export const ConnectionLines: React.FC<Props> = ({ mappings }) => {
  return (
    <svg className="absolute inset-0 pointer-events-none">
      {mappings.map((mapping) => {
        const { x1, y1, x2, y2 } = calculateLineCoordinates(
          mapping.source,
          mapping.target
        );

        const color = getLineColor(mapping.confidence);

        return (
          <path
            key={`${mapping.source}-${mapping.target}`}
            d={`M ${x1} ${y1} C ${x1 + 100} ${y1}, ${x2 - 100} ${y2}, ${x2} ${y2}`}
            stroke={color}
            strokeWidth={2}
            fill="none"
            className="transition-all duration-300"
          />
        );
      })}
    </svg>
  );
};

// lineCalculations.ts
export const calculateLineCoordinates = (
  sourceId: string,
  targetId: string
) => {
  const sourceEl = document.getElementById(`source-${sourceId}`);
  const targetEl = document.getElementById(`target-${targetId}`);

  if (!sourceEl || !targetEl) return null;

  const sourceRect = sourceEl.getBoundingClientRect();
  const targetRect = targetEl.getBoundingClientRect();

  return {
    x1: sourceRect.right,
    y1: sourceRect.top + sourceRect.height / 2,
    x2: targetRect.left,
    y2: targetRect.top + targetRect.height / 2
  };
};

export const getLineColor = (confidence: number): string => {
  if (confidence >= 0.95) return '#10B981'; // green
  if (confidence >= 0.80) return '#F59E0B'; // yellow
  return '#9CA3AF'; // gray
};
```

## Integration Checkpoints

### Day 1 EOD
- ✅ Share MappingConfig data structure with Module 1 & 3
- ✅ Document mapping state format

### Day 3 EOD
- ✅ Test with real auto-map API (Module 4)
- ✅ Verify mapping accuracy
- ✅ Handle API errors gracefully

### Day 4 EOD
- ✅ Test with real validation API (Module 3)
- ✅ Verify validation messages display correctly

### Day 5 EOD
- ✅ Full integration test with all modules
- ✅ End-to-end mapping workflow
- ✅ Bug fixing session with team

## Success Criteria

### Functional Requirements
- ✅ Drag-and-drop works smoothly
- ✅ Visual connection lines display correctly
- ✅ Auto-map finds 80%+ of fields
- ✅ Color-coding shows confidence levels
- ✅ Validation shows errors/warnings
- ✅ Progress bar updates correctly
- ✅ Can undo mappings
- ✅ Required fields are clearly marked

### Non-Functional Requirements
- ✅ Smooth, fluid animations
- ✅ Intuitive drag interactions
- ✅ Visual feedback at every step
- ✅ Fast performance (no lag)
- ✅ Beautiful, polished UI

### Code Quality
- ✅ Reusable components
- ✅ Clean separation of concerns
- ✅ Proper TypeScript types
- ✅ Performant (React.memo, useMemo)
- ✅ Well-commented SVG logic

## Common Pitfalls to Avoid
1. ❌ Don't recalculate line coordinates on every render - use memoization
2. ❌ Don't skip visual feedback - users need to see what's happening
3. ❌ Don't allow invalid mappings (same source to multiple targets)
4. ❌ Don't forget to handle window resize (lines need to update)
5. ❌ Don't make drag targets too small - min 40x40px for usability

## Performance Optimization

```typescript
// Use React.memo for field cards
export const FieldCard = React.memo<Props>(({ field }) => {
  // Component logic
});

// Use useMemo for line calculations
const lines = useMemo(() => {
  return mappings.map(mapping => calculateLineCoordinates(
    mapping.source,
    mapping.target
  ));
}, [mappings]);

// Debounce window resize handler
const debouncedResize = useDebouncedCallback(() => {
  recalculateLines();
}, 100);
```

## Resources
- [@dnd-kit Documentation](https://docs.dndkit.com/)
- [React DnD Documentation](https://react-dnd.github.io/react-dnd/)
- [SVG Path Tutorial](https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Paths)
- [Bézier Curves](https://javascript.info/bezier-curve)
- [Framer Motion](https://www.framer.com/motion/)

## Questions or Blockers?
- **Module 1 (Core UI)**: For AppContext or component props
- **Module 3 (Transform)**: For validation API or data format
- **Module 4 (Auto-Map)**: For auto-map API or mapping algorithm
- **Team Chat**: For quick questions or help requests
- **Daily Standup**: For status updates and coordination

---

**Remember**: This is the "WOW" feature that wins the demo! Focus on:
1. **Visual Impact**: Beautiful, animated connection lines
2. **Magic Moment**: Auto-map button that "just works"
3. **Intuitive**: Drag-and-drop that feels natural
4. **Polish**: Smooth animations, clear feedback

This is where judges will be impressed. Make it amazing! 🎨✨
