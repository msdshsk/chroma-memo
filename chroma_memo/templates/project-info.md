# Project Knowledge Management

Show project information and manage knowledge base based on user requests.

## Instructions
$ARGUMENTS

## Task
Based on the user's request above, provide project information or manage the knowledge base using appropriate commands.

## Available Commands

### List all projects
```bash
chroma-memo projects
```

### Show project information and statistics
```bash
chroma-memo info {project_name}
```

### List all knowledge in this project
```bash
chroma-memo list {project_name}
```

### Delete specific knowledge entry
```bash
chroma-memo del {project_name} "[ENTRY_ID]" --confirm
```

## Examples of Instructions and Responses

### Example 1: "プロジェクトの情報を教えて"
1. Show project statistics and details
2. Execute: `chroma-memo info {project_name}`

### Example 2: "どんなナレッジが保存されているか見せて"
1. List all knowledge entries in the project
2. Execute: `chroma-memo list {project_name}`

### Example 3: "他にどんなプロジェクトがあるか知りたい"
1. Show all available projects
2. Execute: `chroma-memo projects`

### Example 4: "IDが〇〇のナレッジを削除して"
1. Delete the specific entry by ID
2. Execute: `chroma-memo del {project_name} "[SPECIFIED_ID]" --confirm`

### Example 5: "全体的な統計情報が欲しい"
1. Show project info and list entries for overview
2. Execute: `chroma-memo info {project_name}` then `chroma-memo list {project_name}`

## Process
1. Understand the user's request in $ARGUMENTS
2. Determine which information or action is needed
3. Execute the appropriate chroma-memo command(s)
4. Present the results in a clear, organized format