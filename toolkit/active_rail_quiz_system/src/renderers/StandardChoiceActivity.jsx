import { RichText } from "../components/RichText.jsx";

export function StandardChoiceActivity({ question, response, onResponse }) {
  const inputType = question.type === "multi" ? "checkbox" : "radio";
  const selected = response?.choices || [];

  function toggle(choiceId) {
    if (question.type === "multi") {
      const next = selected.includes(choiceId)
        ? selected.filter((id) => id !== choiceId)
        : [...selected, choiceId];
      onResponse({ ...response, choices: next });
      return;
    }
    onResponse({ ...response, choices: [choiceId] });
  }

  return (
    <>
      <div className="prompt"><RichText content={question.prompt} /></div>
      <div className="options">
        {question.choices.map((choice) => (
          <label className="option" key={choice.id}>
            <input
              type={inputType}
              name={question.id}
              checked={selected.includes(choice.id)}
              onChange={() => toggle(choice.id)}
            />
            <span><RichText content={choice.content} /></span>
          </label>
        ))}
      </div>
    </>
  );
}
