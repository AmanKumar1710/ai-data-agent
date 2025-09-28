import React, { useState } from "react";

export default function App() {
  const [file, setFile] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [aiAnswer, setAiAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onFileChange = (e) => {
    setFile(e.target.files[0]);
    setPreviewData(null);
    setAnswer("");
    setAiAnswer(null);
    setError("");
  };

  const uploadFile = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch("http://localhost:8000/upload/", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (res.ok) {
        setPreviewData({
          columns: data.columns,
          preview: data.preview,
          filename: data.filename,
        });
      } else {
        setError(data.error || "Error uploading file.");
      }
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  const askQuestion = async (useAI = false) => {
    if (!previewData || !question.trim()) return;
    setLoading(true);
    setAnswer("");
    setAiAnswer(null);
    setError("");
    let url = useAI ? "http://localhost:8000/llm_question/" : "http://localhost:8000/question/";
    try {
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: previewData.filename, question }),
      });
      const data = await res.json();
      if (res.ok) {
        if (useAI) {
          setAiAnswer(data);
        } else {
          setAnswer(data.answer);
        }
      } else {
        setError(data.error || "Error answering question.");
      }
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 650, margin: "auto", padding: 20, fontFamily: "Segoe UI, Tahoma, Geneva, Verdana, sans-serif" }}>
      <h2 style={{ textAlign: "center" }}>AI Data Agent – Upload Excel File</h2>

      <input type="file" onChange={onFileChange} accept=".xls,.xlsx" />
      <button onClick={uploadFile} disabled={!file || loading} style={{ marginLeft: 10 }}>
        Upload
      </button>

      {loading && <p style={{ color: "blue" }}>Processing...</p>}

      {error && <p style={{ color: "red", marginTop: 10 }}>{error}</p>}

      {previewData && (
        <>
          <h3 style={{ marginTop: 20 }}>Data Preview</h3>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
            <thead>
              <tr>
                {previewData.columns.map((col) => (
                  <th key={col} style={{ border: "1px solid #ccc", padding: 6, background: "#f0f0f0" }}>{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {previewData.preview.map((row, idx) => (
                <tr key={idx}>
                  {previewData.columns.map((col) => (
                    <td key={col} style={{ border: "1px solid #ccc", padding: 6 }}>{row[col]}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>

          <h3 style={{ marginTop: 30 }}>Ask a Question About Your Data</h3>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="E.g: What is the average age?"
            style={{ width: "70%", padding: 8, fontSize: 14 }}
          />
          <button onClick={() => askQuestion(false)} disabled={!question.trim() || loading} style={{ marginLeft: 10 }}>
            Ask
          </button>
          <button onClick={() => askQuestion(true)} disabled={!question.trim() || loading} style={{ marginLeft: 10 }}>
            Smart AI Answer
          </button>

          {answer && (
            <div style={{ marginTop: 20 }}>
              <strong>Answer:</strong>
              <p>{answer}</p>
            </div>
          )}

          {aiAnswer && (
            <div style={{ marginTop: 20 }}>
              <strong>AI Answer:</strong>
              <pre style={{ background: "#272822", color: "#f8f8f2", padding: 12, borderRadius: 5, overflowX: "auto" }}>
                {aiAnswer.answer}
              </pre>
              <code style={{ display: "block", whiteSpace: "pre-wrap", background: "#eee", padding: 10, borderRadius: 4, marginTop: 10 }}>
                {aiAnswer.code}
              </code>
            </div>
          )}
        </>
      )}
    </div>
  );
}
