import { RichText } from "../components/RichText.jsx";

export function MatchingActivity({ question, response, onResponse }) {
  const matches = response?.matches || {};

  function choose(promptId, optionId) {
    onResponse({ ...response, matches: { ...matches, [promptId]: optionId } });
  }

  return (
    <div className="matching-surface">
      <div className="prompt"><RichText content={question.prompt} /></div>
      <div className="matching-grid">
        {question.prompts.map((prompt) => (
          <div className="matching-row" key={prompt.id}>
            <div className="matching-prompt"><RichText content={prompt.content} /></div>
            <select value={matches[prompt.id] || ""} onChange={(event) => choose(prompt.id, event.target.value)}>
              <option value="">Choose match</option>
              {question.options.map((option) => (
                <option value={option.id} key={option.id}>{option.label}</option>
              ))}
            </select>
          </div>
        ))}
      </div>
    </div>
  );
}
