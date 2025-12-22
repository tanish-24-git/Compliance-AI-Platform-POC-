# Frontend Architecture

## Overview
The frontend is built with **React**, **TypeScript**, and **Tailwind CSS**. It provides a modern, responsive interface for Insurance Agents to generate content and for Compliance Officers to manage rules.

## Directory Structure
```text
src/
├── components/
│   ├── agent/         # Agent-specific components (ChatInterface)
│   ├── admin/         # Admin components (RuleList, RuleStats)
│   └── common/        # Shared UI components (Button, Card, Input)
├── pages/
│   ├── AgentPage.tsx  # Main content generation view
│   ├── AdminPage.tsx  # Compliance dashboard view
│   └── HomePage.tsx   # Landing page
├── services/
│   └── api.ts         # Axios instance and API methods
└── types/             # TypeScript interfaces
```

## Core Components

### `ChatInterface` (`components/agent`)
The primary interaction point for agents.
- **State**: Manages chat history, prompt input, and generation loading state.
- **Actions**: Calls `generateContent` API.
- **Visualization**: Renders the AI's response and compliance score (Safe/Violations).

### `RuleManagement` (`components/admin`)
Dashboard for compliance officers.
- **Features**: View, Create, Edit, Deactivate rules.
- **Upload**: PDF upload for automated rule extraction.

## State Management
- Local React state (`useState`) is used for component-level data.
- API calls use a centralized `api.ts` service layer for consistent error handling and typing.

## Styling
- **Tailwind CSS** is used for utility-first styling.
- Design tokens (colors, spacing) are consistent with the "Premium/Trust" insurance aesthetic (Blues, Whites, Clean Grays).

## Integration
The frontend communicates with the backend via REST API at `http://localhost:8000/api/v1`.
- **Authentication**: JWT-based (mocked/simplified for POC).
- **Validation**: Pydantic validation errors from backend are parsed and displayed via toast notifications or inline errors.
