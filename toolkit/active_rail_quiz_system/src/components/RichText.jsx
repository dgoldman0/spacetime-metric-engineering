import { MathInline } from "./Math.jsx";

export function RichText({ content }) {
  if (content == null) return null;
  if (typeof content === "string") return <>{content}</>;
  return (
    <>
      {content.map((part, index) => {
        if (typeof part === "string") return <span key={index}>{part}</span>;
        if (part.type === "math") {
          return <MathInline key={index} latex={part.latex} label={part.label} />;
        }
        return <span key={index}>{part.text}</span>;
      })}
    </>
  );
}
