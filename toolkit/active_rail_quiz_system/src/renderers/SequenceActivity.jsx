import { RichText } from "../components/RichText.jsx";

export function SequenceActivity({ question, response, onResponse }) {
  const order = response?.order || question.items.map((item) => item.id);

  function move(index, direction) {
    const target = direction === "up" ? index - 1 : index + 1;
    if (target < 0 || target >= order.length) return;
    const next = [...order];
    [next[index], next[target]] = [next[target], next[index]];
    onResponse({ ...response, order: next });
  }

  return (
    <div className="chronology-surface">
      <div className="prompt"><RichText content={question.prompt} /></div>
      <ol className="sequence-list">
        {order.map((itemId, index) => {
          const item = question.items.find((candidate) => candidate.id === itemId);
          return (
            <li className="sequence-item" key={itemId}>
              <span className="sequence-index">{index + 1}</span>
              <span><RichText content={item.content} /></span>
              <button type="button" className="mini-button" onClick={() => move(index, "up")}>Move up</button>
              <button type="button" className="mini-button" onClick={() => move(index, "down")}>Move down</button>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
