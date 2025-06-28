# Knowledge Maintenance

Maintain and update knowledge in the current project's knowledge base based on user instructions.

## Instructions
$ARGUMENTS

## Task
Based on the user's maintenance request above, help them update, clean up, or reorganize their knowledge base using appropriate commands.

## Available Commands

### Search for existing knowledge
```bash
chroma-memo search {project_name} "[SEARCH_TERMS]" --max-results [NUMBER]
```

### List all knowledge
```bash
chroma-memo list {project_name}
```

### Delete specific knowledge
```bash
chroma-memo del {project_name} "[ENTRY_ID]" --confirm
```

### Add updated knowledge
```bash
chroma-memo add {project_name} "[NEW_CONTENT]" --tags [TAGS]
```

## Examples of Instructions and Responses

### Example 1: "古いReact情報を新しい情報に更新して"
1. Search for React-related knowledge: `chroma-memo search {project_name} "react" --max-results 10`
2. Identify outdated entries from the results
3. Delete old entries: `chroma-memo del {project_name} "[OLD_ENTRY_ID]" --confirm`
4. Add updated knowledge: `chroma-memo add {project_name} "Updated React best practices for 2024" --tags react frontend updated`

### Example 2: "重複しているナレッジを整理して"
1. List all knowledge: `chroma-memo list {project_name}`
2. Search for potential duplicates: `chroma-memo search {project_name} "[TOPIC]" --max-results 20`
3. Remove duplicate entries: `chroma-memo del {project_name} "[DUPLICATE_ID]" --confirm`
4. Keep the best version or create a consolidated entry

### Example 3: "〇〇に関する間違った情報を削除して"
1. Search for the topic: `chroma-memo search {project_name} "〇〇" --max-results 15`
2. Review results to identify incorrect information
3. Delete incorrect entries: `chroma-memo del {project_name} "[INCORRECT_ID]" --confirm`
4. Optionally add correct information: `chroma-memo add {project_name} "[CORRECT_INFO]" --tags corrected [TOPIC]`

### Example 4: "タグを整理して統一したい"
1. List all entries: `chroma-memo list {project_name}`
2. Identify entries with inconsistent tags
3. For each entry: Delete old → Add with corrected tags
4. Example: `chroma-memo del {project_name} "[ID]" --confirm` then `chroma-memo add {project_name} "[CONTENT]" --tags [STANDARDIZED_TAGS]`

## Maintenance Process
1. Understand the user's maintenance request in $ARGUMENTS
2. Search for relevant knowledge entries
3. Identify what needs to be updated, removed, or reorganized
4. Execute appropriate delete/add commands
5. Provide a summary of changes made