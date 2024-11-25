import "./App.css";
import axios from "axios";
import { useState, useEffect } from "react";
import * as pdfjsLib from "pdfjs-dist/webpack";

function App() {
  const [urlProcess, setUrlProcess] = useState(false);
  const [queryProcess, setQueryProcess] = useState(false);
  const [taskID, setTaskID] = useState("");
  const [isPolling, setIsPolling] = useState(false);
  const [taskData, setTaskData] = useState(null);
  const [showResources, setShowResources] = useState(false);

  const [url, setUrl] = useState("");

  const [jobScrapeUrl, setJobScrapeUrl] = useState("");
  const [jobScrapeTaskID, setJobScrapeTaskID] = useState("");
  const [jobScrapeTaskData, setJobScrapeTaskData] = useState(null);
  const [jobScrapeProcess, setJobScrapeProcess] = useState(false);
  const [isPollingJob, setIsPollingJob] = useState(false);

  const [text, setText] = useState("");
  const [jobResults, setJobResults] = useState(null);

  const [myQuery, setMyQuery] = useState("");
  const [ragResult, setRagResult] = useState(null);

  const [isAdmin, setIsAdmin] = useState(false);

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

  // Effect hook for polling when taskID is set
  useEffect(() => {
    let interval;

    // Start polling if taskID is not empty
    if (jobScrapeTaskID && !isPollingJob) {
      setIsPollingJob(true);

      interval = setInterval(async () => {
        try {
          // Replace with your actual endpoint
          const response = await axios.get(
            `http://127.0.0.1:5000/task-status/${taskID}`
          );
          setJobScrapeTaskData(response.data);

          // Optionally, check for some condition to stop polling
          if (response.data.status === "Completed") {
            clearInterval(interval);
            setIsPollingJob(false);
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
      setIsPollingJob(false);
    };
  }, [jobScrapeTaskID]); // Re-run whenever taskID changes

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

  const handleSubmitJobScrape = (e) => {
    e.preventDefault();
    axios
      .post("http://127.0.0.1:5000/scrape-jobs", { url: jobScrapeUrl })
      .then((response) => {
        console.log(response.data);
        setJobScrapeProcess(true);
        setJobScrapeTaskID(response.data["task_id"]);
      })
      .catch((error) => {
        console.error(error);
        setJobScrapeProcess(false);
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

  const handleFileChange = async (event) => {
    event.preventDefault();

    const file = event.target.files[0];
    if (!file) return;

    const fileReader = new FileReader();
    fileReader.onload = async (e) => {
      const typedArray = new Uint8Array(e.target.result);

      // Load PDF
      const pdf = await pdfjsLib.getDocument(typedArray).promise;

      let extractedText = "";

      // Extract text from each page
      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();
        const pageText = textContent.items.map((item) => item.str).join(" ");
        extractedText += pageText + "\n";
      }

      setText(extractedText);
    };

    fileReader.readAsArrayBuffer(file);
  };

  const handleSubmitResume = (e) => {
    e.preventDefault();
    axios
      .post("http://127.0.0.1:5000/resume-match", { resume_text: text })
      .then((response) => {
        console.log(response.data);
        setJobResults(response.data);
      })
      .catch((error) => {
        console.error(error);
      });
  };

  const clearDB = (e, db_name) => {
    e.preventDefault();
    axios
      .post("http://127.0.0.1:5000/clear-db", { index_name: db_name })
      .then((response) => {
        console.log(response.data);
      })
      .catch((error) => {
        console.error(error);
      });
  };

  return (
    <div className="App">
      {/* Left */}
      <div className="left-wall">
        {/* Logo */}
        <div
          style={{
            backgroundColor: "gray",
            width: "40%",
            height: "70px",
            justifyContent: "center",
            alignContent: "center",
            color: "white",
          }}
        >
          <b>Your Company Logo</b>
          <br />
          <span>Powered by Connex</span>
        </div>
        <button
          style={{ marginTop: "5%" }}
          onClick={() => setIsAdmin(!isAdmin)}
        >
          Enable Admin Controls (demo)
        </button>

        {/* ADMIN: Scrape jobs */}
        {isAdmin && (
          <div
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              display: "flex",
              flexDirection: "column",
              gap: 10,
              padding: 10,
              backgroundColor: "black",
              color: "white",
            }}
          >
            <span>Scrape Job Site: Admin Controls</span>
            <button onClick={(e) => clearDB(e, "jobs")}>
              Clear previous scrapes
            </button>
            <form
              style={{ display: "flex", alignItems: "center" }}
              onSubmit={(e) => handleSubmitJobScrape(e)}
            >
              <label id="url">URL:</label>
              <textarea
                value={jobScrapeUrl}
                onChange={(e) => setJobScrapeUrl(e.target.value)}
                style={{ marginInline: "5px" }}
                placeholder="url"
              />
              <button type="submit">Submit</button>
              <span style={{ fontSize: "10px", marginLeft: "5px" }}>
                {jobScrapeProcess ? "Done" : "Not started/failed"}
              </span>
            </form>
            <p>
              {" "}
              {jobScrapeTaskID !== "" && (
                <div>
                  {isPollingJob ? "Polling " : "No longer polling"} task{" "}
                  {jobScrapeTaskID}. Current status:{" "}
                  {jobScrapeTaskData && jobScrapeTaskData["status"]}
                </div>
              )}
            </p>
          </div>
        )}

        {/* Resume checker */}
        <div style={{ marginBlock: "5%" }}>
          <form
            className="resume-checker"
            onSubmit={(e) => handleSubmitResume(e)}
          >
            <label id="resumeUpload">
              Upload your resume, and we will match you to a suitable job!
            </label>
            <input
              type="file"
              accept="application/pdf"
              onChange={handleFileChange}
            />
            <button>Submit</button>
          </form>
        </div>
        {/* Job match results */}
        <div style={{ width: "400px" }} className="resume-checker">
          {jobResults !== null ? (
            <div>
              <p>Here are the matches:</p>
              <ul>
                {jobResults !== null &&
                  jobResults.map((result, idx) => {
                    var source = result[idx.toString()];
                    if ("metadata" in source) {
                      return (
                        <li key={idx}>
                          {idx + 1}: {source["metadata"](0, 200)}{" "}
                          {source["page_content"].substring(0, 200)}
                          {source["page_content"].length >= 200 && "..."}
                        </li>
                      );
                    } else {
                      return (
                        <li key={idx}>
                          {idx + 1}: {source["page_content"].substring(0, 200)}
                          {source["page_content"].length >= 200 && "..."}
                        </li>
                      );
                    }
                  })}
              </ul>
            </div>
          ) : (
            <div>Relevant job descriptions will be displayed here.</div>
          )}
        </div>
      </div>
      {/* Right */}
      <div
        style={{
          height: "100%",
          flex: 1,
          justifyItems: "start",
          position: "relative",
        }}
      >
        {/* Inputs */}
        {/* Admin: Chatbot Controls */}
        {isAdmin && (
          <div
            style={{
              zIndex: 999,
              position: "absolute",
              top: 0,
              right: 0,
              display: "flex",
              flexDirection: "column",
              gap: 10,
              padding: 10,
              backgroundColor: "black",
              color: "white",
            }}
          >
            <span>Chatbot: Admin Controls</span>
            <button onClick={(e) => clearDB(e, "sites")}>
              Clear previous scrapes
            </button>

            <form
              onSubmit={(e) => handleSubmitURL(e)}
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
              }}
            >
              <label id="url">URL:</label>
              <textarea
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                style={{ marginInline: "5px" }}
                placeholder="url"
              />
              <button type="submit">Submit</button>
              <p style={{ fontSize: "10px", marginLeft: "5px" }}>
                {urlProcess ? "Done" : "Not started/failed"}
              </p>
              {taskID !== "" && (
                <div>
                  {isPolling ? "Polling " : "No longer polling"} task {taskID}.
                  Current status: {taskData && taskData["status"]}
                </div>
              )}
            </form>
          </div>
        )}
        <div
          style={{
            position: "relative",
            marginTop: "5%",
            marginLeft: "5%",
            width: "70%",
            fontWeight: 500,
          }}
        >
          <form
            className="chat-bubble"
            onSubmit={(e) => {
              handleSubmitQuery(e);
            }}
          >
            <label id="query">
              Hi! I am Jamie, the assistant for [company name]. How can I help
              you?
            </label>
            <textarea
              onChange={(e) => setMyQuery(e.target.value)}
              style={{ marginInline: "5px" }}
              value={myQuery}
              placeholder="Ask anything"
            />

            <button type="submit">Submit</button>
            <span style={{ fontSize: "10px", marginLeft: "5px" }}>
              {queryProcess ? "Done" : "Not started/failed"}
            </span>
          </form>
        </div>
        {/* Results */}
        <div style={{ position: "relative" }}>
          <div
            style={{
              width: "300px",
              marginTop: "5%",
              marginLeft: "5%",
              backgroundColor: "gray",
              color: "white",
              fontWeight: "500",
            }}
            className="chat-bubble bubble-arrow-2"
          >
            {ragResult !== null ? (
              <div>
                <p>Great question! {ragResult["answer"]}</p>
                <button onClick={() => setShowResources(!showResources)}>
                  Show sources for this result
                </button>
                {showResources && (
                  <>
                    <p>Here are the sources:</p>
                    <ul>
                      {ragResult["similar_results"].length > 0 ? (
                        ragResult["similar_results"].map((result, idx) => {
                          var source = result[idx.toString()];
                          if ("metadata" in source) {
                            return (
                              <li key={idx}>
                                {idx + 1}: {source["metadata"](0, 200)}{" "}
                                {source["page_content"].substring(0, 200)}
                                {source["page_content"].length >= 200 && "..."}
                              </li>
                            );
                          } else {
                            return (
                              <li key={idx}>
                                {idx + 1}:{" "}
                                {source["page_content"].substring(0, 200)}
                                {source["page_content"].length >= 200 && "..."}
                              </li>
                            );
                          }
                        })
                      ) : (
                        <div>
                          None of the scraped resources have a similar result.
                          GPT is answering without context.
                        </div>
                      )}
                    </ul>
                  </>
                )}
              </div>
            ) : (
              <div>
                Your query will be answered based on relevant sources inputted
                by the recruitment team.
              </div>
            )}
          </div>
        </div>
        {/* Recruiter */}
        <img
          style={{
            position: "absolute",
            bottom: "0px",
            right: "10%",
            opacity: 1,
            maxHeight: "70%",
            maxWidth: "100%",
          }}
          src="../images/female-worker.png"
          alt="image"
        />
      </div>
    </div>
  );
}

export default App;
