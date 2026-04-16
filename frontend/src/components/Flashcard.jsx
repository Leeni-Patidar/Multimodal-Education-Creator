export default function Flashcard({ title, image }) {
  return (
    <div className="bg-white shadow-lg rounded-xl p-4 w-64">
      <h3 className="font-bold mb-2">{title}</h3>

      {image && (
        <img
          src={`data:image/png;base64,${image}`}
          alt="flashcard"
          className="rounded"
        />
      )}
    </div>
  );
}