import "./App.css";
import axios from "axios";
import { useState, useEffect } from "react";
function App() {
  const [urlProcess, setUrlProcess] = useState(false);
  const [queryProcess, setQueryProcess] = useState(false);
  const [taskID, setTaskID] = useState("");
  const [isPolling, setIsPolling] = useState(false);
  const [taskData, setTaskData] = useState(null);

  const [url, setUrl] = useState(
    "https://www.graduatesfirst.com/morgan-stanley-job-tests"
  );
  const [myQuery, setMyQuery] = useState("what are morgan stanley's values");
  const [ragResult, setRagResult] = useState(null);

  // Effect hook for polling when taskID is set
  useEffect(() => {
    let interval;

    // Start polling if taskID is not empty
    if (taskID && !isPolling) {
      setIsPolling(true);

      interval = setInterval(async () => {
        try {
          // Replace with your actual endpoint
          const response = await axios.get(
            `http://127.0.0.1:5000/task-status/${taskID}`
          );
          setTaskData(response.data);

          // Optionally, check for some condition to stop polling
          if (response.data.status === "Completed") {
            clearInterval(interval);
            setIsPolling(false);
          }
        } catch (error) {
          console.error("Error fetching task data:", error);
        }
      }, 1000); // Poll every second
    }

    // Clean up the interval if taskID is cleared or component unmounts
    return () => {
      if (interval) {
        clearInterval(interval);
      }
      setIsPolling(false);
    };
  }, [taskID]); // Re-run whenever taskID changes

  const handleSubmitURL = (e) => {
    e.preventDefault();
    axios
      .post("http://127.0.0.1:5000/process-file", { fileURL: url })
      .then((response) => {
        console.log(response.data);
        setUrlProcess(true);
        setTaskID(response.data["task_id"]);
      })
      .catch((error) => {
        console.error(error);
        setUrlProcess(false);
      });
  };

  const handleSubmitQuery = (e) => {
    e.preventDefault();
    axios
      .post("http://127.0.0.1:5000/ask-question", { query: myQuery })
      .then((response) => {
        console.log(response.data);
        setRagResult(response.data);
        setQueryProcess(true);
      })
      .catch((error) => {
        console.error(error);
        setQueryProcess(false);
      });
  };

  return (
    <div className="App">
      <form onSubmit={(e) => handleSubmitURL(e)}>
        <label id="url">URL:</label>
        <textarea
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          style={{ marginInline: "5px" }}
          placeholder="url"
        />
        <button type="submit">Submit</button>
        <span style={{ fontSize: "10px", marginLeft: "5px" }}>
          {urlProcess ? "Done" : "Not started/failed"}
        </span>
      </form>

      <form
        onSubmit={(e) => {
          handleSubmitQuery(e);
        }}
      >
        <label id="query">Query:</label>
        <textarea
          onChange={(e) => setMyQuery(e.target.value)}
          style={{ marginInline: "5px" }}
          value={myQuery}
          placeholder="my query"
        />

        <button type="submit">Submit</button>
        <span style={{ fontSize: "10px", marginLeft: "5px" }}>
          {queryProcess ? "Done" : "Not started/failed"}
        </span>
      </form>
      <div style={{ display: "flex", maxWidth: "500px" }}>
        {ragResult !== null ? (
          <div>
            <p>GPT says: {ragResult["answer"]}</p>
            <p>Here are the sources:</p>
            <ul>
              {ragResult["similar_results"].map((result, idx) => {
                var source = result[idx.toString()];
                return (
                  <li key={idx}>
                    {idx + 1}: {source.substring(0, 200)}
                    {source.length >= 100 && "..."}
                  </li>
                );
              })}
            </ul>
          </div>
        ) : (
          <div>
            {taskID != "" && (
              <div>
                {isPolling ? "Polling " : "No longer polling"} task {taskID}.
                Current status: {taskData && taskData["status"]}
              </div>
            )}
            Scrape a website and ask a question about it!
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
