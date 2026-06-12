import { useState } from 'react';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { AnalyzeProperty } from './pages/AnalyzeProperty';
import { Runs } from './pages/Runs';
import { Portfolio } from './pages/Portfolio';
import { ResearchLab } from './pages/ResearchLab';
import { Settings } from './pages/Settings';

export type Page = 'dashboard' | 'analyze' | 'runs' | 'portfolio' | 'research' | 'settings';

export default function App() {
  const [page, setPage] = useState<Page>('dashboard');
  const content =
    page === 'dashboard' ? <Dashboard onNavigate={setPage} /> :
    page === 'analyze' ? <AnalyzeProperty /> :
    page === 'runs' ? <Runs /> :
    page === 'portfolio' ? <Portfolio /> :
    page === 'research' ? <ResearchLab /> : <Settings />;
  return <Layout page={page} onPageChange={setPage}>{content}</Layout>;
}
