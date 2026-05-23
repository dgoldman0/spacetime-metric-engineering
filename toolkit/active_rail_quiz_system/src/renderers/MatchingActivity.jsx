import { RichText } from "../components/RichText.jsx";
import { orderByIds } from "../lib/session.js";

export function MatchingActivity({ question, response, onResponse }) {
  const matches = response?.matches || {};
  const prompts = orderByIds(question.prompts, response?.promptOrder);
  const options = orderByIds(question.options, response?.optionOrder);

  function choose(promptId, optionId) {
    onResponse({ ...response, matches: { ...matches, [promptId]: optionId } });
  }

  return (
    <div className="matching-surface">
      <div className="prompt"><RichText content={question.prompt} /></div>
      <div className="matching-grid">
        {prompts.map((prompt) => (
          <div className="matching-row" key={prompt.id}>
            <div className="matching-prompt"><RichText content={prompt.content} /></div>
            <select value={matches[prompt.id] || ""} onChange={(event) => choose(prompt.id, event.target.value)}>
              <option value="">Choose match</option>
              {options.map((option) => (
                <option value={option.id} key={option.id}>{option.label}</option>
              ))}
            </select>
          </div>
        ))}
      </div>
    </div>
  );
}
