import { useState } from "react";
import { RichText } from "../components/RichText.jsx";

export function SequenceActivity({ question, response, onResponse }) {
  const [draggingId, setDraggingId] = useState(null);
  const order = response?.order || question.items.map((item) => item.id);

  function move(index, direction) {
    const target = direction === "up" ? index - 1 : index + 1;
    if (target < 0 || target >= order.length) return;
    const next = [...order];
    [next[index], next[target]] = [next[target], next[index]];
    onResponse({ ...response, order: next });
  }

  function reorder(sourceId, targetId) {
    if (!sourceId || !targetId || sourceId === targetId) return;
    const sourceIndex = order.indexOf(sourceId);
    const targetIndex = order.indexOf(targetId);
    if (sourceIndex < 0 || targetIndex < 0) return;

    const next = [...order];
    const [moved] = next.splice(sourceIndex, 1);
    next.splice(targetIndex, 0, moved);
    onResponse({ ...response, order: next });
  }

  function handleDragStart(event, itemId) {
    setDraggingId(itemId);
    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.setData("text/plain", itemId);
  }

  function handleDragOver(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }

  function handleDrop(event, targetId) {
    event.preventDefault();
    const sourceId = event.dataTransfer.getData("text/plain") || draggingId;
    reorder(sourceId, targetId);
    setDraggingId(null);
  }

  function handleKeyDown(event, index) {
    if (event.key === "ArrowUp" || event.key === "ArrowLeft") {
      event.preventDefault();
      move(index, "up");
    }
    if (event.key === "ArrowDown" || event.key === "ArrowRight") {
      event.preventDefault();
      move(index, "down");
    }
  }

  return (
    <div className="chronology-surface">
      <div className="prompt"><RichText content={question.prompt} /></div>
      <ol className="sequence-list">
        {order.map((itemId, index) => {
          const item = question.items.find((candidate) => candidate.id === itemId);
          return (
            <li
              className={`sequence-item ${draggingId === itemId ? "dragging" : ""}`}
              key={itemId}
              draggable
              tabIndex={0}
              title="Drag to reorder. Use arrow keys while focused."
              aria-label={`Position ${index + 1}: drag to reorder`}
              onDragStart={(event) => handleDragStart(event, itemId)}
              onDragOver={handleDragOver}
              onDrop={(event) => handleDrop(event, itemId)}
              onDragEnd={() => setDraggingId(null)}
              onKeyDown={(event) => handleKeyDown(event, index)}
            >
              <span className="sequence-index">{index + 1}</span>
              <span className="sequence-grip" aria-hidden="true">::</span>
              <span><RichText content={item.content} /></span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
