import React, { useState } from "react";
import {
  Container, Typography, TextField, Button, Box, Paper, CircularProgress, Alert, Tabs, Tab
} from "@mui/material";
import axios from "axios";

// const API_URL = "http://localhost:5100";
const API_URL = "http://34.47.234.81:5100";
const AGENT_API_KEY = "5acd6f98c443e42bb1631cb6bcd26dc8a2202f0d3a24e31c5090efa69953e849";

function App() {
  const [tab, setTab] = useState(0);

  // Shared
  const [jobId, setJobId] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Schedule
  const [task, setTask] = useState("");
  const [scheduleResult, setScheduleResult] = useState(null);

  // Status
  const [status, setStatus] = useState(null);

  // Shell
  const [command, setCommand] = useState("");
  const [shellResult, setShellResult] = useState(null);

  // Code Exec
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [codeResult, setCodeResult] = useState(null);

  // Context
  const [contextData, setContextData] = useState("");
  const [contextResult, setContextResult] = useState(null);

  // Tab handler
  const handleTabChange = (e, newValue) => {
    setTab(newValue);
    setError("");
    setLoading(false);
  };

  // API handlers
  const handleApi = async (fn) => {
    setError("");
    setLoading(true);
    try {
      await fn();
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
    }
    setLoading(false);
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>Agent Orchestration UI</Typography>
        <Tabs value={tab} onChange={handleTabChange} sx={{ mb: 2 }}>
          <Tab label="Schedule" />
          <Tab label="Status" />
          <Tab label="Shell" />
          <Tab label="Code Exec" />
          <Tab label="Context" />
        </Tabs>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {loading && <Box sx={{ display: "flex", justifyContent: "center", mb: 2 }}><CircularProgress /></Box>}

        {/* Schedule Tab */}
        {tab === 0 && (
          <Box>
            <TextField label="Task" value={task} onChange={e => setTask(e.target.value)} fullWidth sx={{ mb: 2 }} />
            <Button variant="contained" onClick={() => handleApi(async () => {
              const resp = await axios.post(`${API_URL}/schedule`, { task });
              setScheduleResult(resp.data);
              setJobId(resp.data.job_id);
            })}>Schedule Job</Button>
            {scheduleResult && <Alert sx={{ mt: 2 }}>Job ID: {scheduleResult.job_id}</Alert>}
          </Box>
        )}

        {/* Status Tab */}
        {tab === 1 && (
          <Box>
            <TextField label="Job ID" value={jobId} onChange={e => setJobId(e.target.value)} fullWidth sx={{ mb: 2 }} />
            <Button variant="contained" onClick={() => handleApi(async () => {
              const resp = await axios.get(`${API_URL}/status/${jobId}`);
              setStatus(resp.data);
            })}>Check Status</Button>
            {status && <Paper sx={{ mt: 2, p: 2, bgcolor: "#f5f5f5" }}><pre>{JSON.stringify(status, null, 2)}</pre></Paper>}
          </Box>
        )}

        {/* Shell Tab */}
        {tab === 2 && (
          <Box>
            <TextField label="Job ID" value={jobId} onChange={e => setJobId(e.target.value)} fullWidth sx={{ mb: 2 }} />
            <TextField label="Shell Command" value={command} onChange={e => setCommand(e.target.value)} fullWidth sx={{ mb: 2 }} />
            <Button variant="contained" onClick={() => handleApi(async () => {
              const resp = await axios.post(
                `${API_URL}/proxy/${jobId}/shell/exec`,
                { command },
                { headers: { "X-API-Key": AGENT_API_KEY } }
              );
              setShellResult(resp.data);
            })}>Run Shell</Button>
            {shellResult && <Paper sx={{ mt: 2, p: 2, bgcolor: "#f5f5f5" }}><pre>{JSON.stringify(shellResult, null, 2)}</pre></Paper>}
          </Box>
        )}

        {/* Code Exec Tab */}
        {tab === 3 && (
          <Box>
            <TextField label="Job ID" value={jobId} onChange={e => setJobId(e.target.value)} fullWidth sx={{ mb: 2 }} />
            <TextField
              label="Code"
              value={code}
              onChange={e => setCode(e.target.value)}
              fullWidth
              multiline
              minRows={4}
              sx={{ mb: 2 }}
            />
            <TextField
              select
              label="Language"
              value={language}
              onChange={e => setLanguage(e.target.value)}
              SelectProps={{ native: true }}
              sx={{ mb: 2, width: 200 }}
            >
              <option value="python">Python</option>
              <option value="typescript">TypeScript</option>
            </TextField>
            <Button variant="contained" onClick={() => handleApi(async () => {
              const resp = await axios.post(
                `${API_URL}/proxy/${jobId}/code/exec`,
                { code, language },
                { headers: { "X-API-Key": AGENT_API_KEY } }
              );
              setCodeResult(resp.data);
            })}>Run Code</Button>
            {codeResult && <Paper sx={{ mt: 2, p: 2, bgcolor: "#f5f5f5" }}><pre>{JSON.stringify(codeResult, null, 2)}</pre></Paper>}
          </Box>
        )}

        {/* Context Tab */}
        {tab === 4 && (
          <Box>
            <TextField label="Job ID" value={jobId} onChange={e => setJobId(e.target.value)} fullWidth sx={{ mb: 2 }} />
            <TextField
              label="Context Data (JSON)"
              value={contextData}
              onChange={e => setContextData(e.target.value)}
              fullWidth
              multiline
              minRows={2}
              sx={{ mb: 2 }}
            />
            <Button variant="contained" sx={{ mr: 2 }} onClick={() => handleApi(async () => {
              const resp = await axios.post(
                `${API_URL}/proxy/${jobId}/context/save`,
                { job_id: jobId, context: JSON.parse(contextData) },
                { headers: { "X-API-Key": AGENT_API_KEY } }
              );
              setContextResult(resp.data);
            })}>Save Context</Button>
            <Button variant="outlined" sx={{ mr: 2 }} onClick={() => handleApi(async () => {
              const resp = await axios.get(
                `${API_URL}/proxy/${jobId}/context/load`,
                { headers: { "X-API-Key": AGENT_API_KEY }, params: { job_id: jobId } }
              );
              setContextResult(resp.data);
            })}>Load Context</Button>
            <Button variant="outlined" onClick={() => handleApi(async () => {
              const resp = await axios.post(
                `${API_URL}/proxy/${jobId}/context/prune`,
                { job_id: jobId, max_tokens: 50 },
                { headers: { "X-API-Key": AGENT_API_KEY } }
              );
              setContextResult(resp.data);
            })}>Prune Context</Button>
            {contextResult && <Paper sx={{ mt: 2, p: 2, bgcolor: "#f5f5f5" }}><pre>{JSON.stringify(contextResult, null, 2)}</pre></Paper>}
          </Box>
        )}
      </Paper>
    </Container>
  );
}

export default App;
