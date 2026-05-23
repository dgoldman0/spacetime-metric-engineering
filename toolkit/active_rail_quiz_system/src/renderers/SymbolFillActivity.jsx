import { useState } from "react";
import { RichText } from "../components/RichText.jsx";

export function SymbolFillActivity({ question, response, onResponse }) {
  const [selectedToken, setSelectedToken] = useState(null);
  const blanks = response?.blanks || {};

  function placeToken(blankId, tokenId) {
    onResponse({ ...response, blanks: { ...blanks, [blankId]: tokenId } });
  }

  function blankContent(blankId) {
    const token = question.tokens.find((candidate) => candidate.id === blanks[blankId]);
    return token ? <RichText content={token.content} /> : "blank";
  }

  return (
    <div className="symbol-surface">
      <div className="prompt">
        {question.promptParts.map((part, index) => {
          if (typeof part === "string") return <span key={index}>{part}</span>;
          if (part.type === "math") return <RichText key={index} content={[part]} />;
          if (part.type === "blank") {
            return (
              <button
                type="button"
                className={`blank ${blanks[part.id] ? "filled" : ""}`}
                key={index}
                onClick={() => selectedToken && placeToken(part.id, selectedToken)}
                onDragOver={(event) => event.preventDefault()}
                onDrop={(event) => {
                  event.preventDefault();
                  const tokenId = event.dataTransfer.getData("text/plain");
                  if (tokenId) placeToken(part.id, tokenId);
                }}
              >
                {blankContent(part.id)}
              </button>
            );
          }
          return null;
        })}
      </div>

      <div className="token-bank" aria-label="Word bank">
        {question.tokens.map((token) => (
          <button
            type="button"
            className={`token ${selectedToken === token.id ? "selected" : ""}`}
            key={token.id}
            draggable
            onClick={() => setSelectedToken(token.id)}
            onDragStart={(event) => event.dataTransfer.setData("text/plain", token.id)}
          >
            <RichText content={token.content} />
          </button>
        ))}
      </div>
      <p className="muted">Drag a rendered token into a blank, or click a token and then click a blank.</p>
    </div>
  );
}
