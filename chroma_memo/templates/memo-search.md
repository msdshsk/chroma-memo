# Search Chroma-Memo Knowledge

Search for relevant knowledge in the current project's knowledge base based on user requests.

## Instructions
$ARGUMENTS

## Task
Based on the user's search request above, find relevant knowledge from the knowledge base using appropriate search terms and commands.

## Available Commands

### Search knowledge
```bash
chroma-memo search {project_name} "[SEARCH_TERMS]" --max-results [NUMBER]
```

### List all knowledge
```bash
chroma-memo list {project_name}
```

## Examples of Instructions and Responses

### Example 1: "React関連のナレッジを探して"
1. Identify relevant search terms: "react", "React", "hooks", "components"
2. Execute: `chroma-memo search {project_name} "react" --max-results 10`

### Example 2: "データベース最適化についての情報はある？"
1. Extract search terms: "database", "optimization", "performance"
2. Execute: `chroma-memo search {project_name} "database optimization" --max-results 5`

### Example 3: "エラー処理に関するナレッジを見たい"
1. Search terms: "error", "exception", "handling", "try-catch"
2. Execute: `chroma-memo search {project_name} "error handling" --max-results 8`

### Example 4: "どんなナレッジがあるか全部見せて"
1. Use list command to show all entries
2. Execute: `chroma-memo list {project_name}`

## Process
1. Understand the user's search request in $ARGUMENTS
2. Extract relevant keywords and search terms
3. Determine appropriate search parameters (max-results)
4. Execute the most suitable chroma-memo search command
5. Present the results to the user