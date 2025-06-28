# Add Knowledge to Chroma-Memo

Add new knowledge to the current project's knowledge base based on user instructions.

## Instructions
$ARGUMENTS

## Task
Based on the user's instructions above, extract or create knowledge content and add it to the knowledge base using the appropriate chroma-memo command.

## Available Commands

### Add knowledge with content
```bash
chroma-memo add {project_name} "[EXTRACTED_CONTENT]" --tags [RELEVANT_TAGS]
```

## Examples of Instructions and Responses

### Example 1: "履歴の内容から要約したものをナレッジにして"
1. Review the conversation history
2. Extract key technical insights or solutions
3. Execute: `chroma-memo add {project_name} "Summary of key technical insights from conversation" --tags summary technical`

### Example 2: "React Hooksについてナレッジに保存しておいて"
1. Create content about React Hooks
2. Execute: `chroma-memo add {project_name} "React Hooks: useState and useEffect for state management and side effects" --tags react hooks frontend`

### Example 3: "この実装方法をナレッジに追加"
1. Analyze the implementation in context
2. Document the approach and key points
3. Execute: `chroma-memo add {project_name} "[IMPLEMENTATION_DESCRIPTION]" --tags implementation [TECH_STACK]`

## Process
1. Understand the user's request in $ARGUMENTS
2. Extract or create relevant knowledge content
3. Choose appropriate tags
4. Execute the chroma-memo add command with the processed content