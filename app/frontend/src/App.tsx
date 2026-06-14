import { Route, Routes } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { AnalyzeProperty } from './pages/AnalyzeProperty';
import { Runs } from './pages/Runs';
import { RunDetail } from './pages/RunDetail';
import { Committee } from './pages/Committee';
import { Portfolio } from './pages/Portfolio';
import { ResearchLab } from './pages/ResearchLab';
import { Tools } from './pages/Tools';
import { Settings } from './pages/Settings';

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/analyze" element={<AnalyzeProperty />} />
        <Route path="/runs" element={<Runs />} />
        <Route path="/runs/:runId" element={<RunDetail />} />
        <Route path="/committee" element={<Committee />} />
        <Route path="/portfolio" element={<Portfolio />} />
        <Route path="/research" element={<ResearchLab />} />
        <Route path="/tools" element={<Tools />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  );
}
