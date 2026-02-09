import { Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Landing from './pages/Landing';
import Connectors from './pages/Connectors';
import Extensions from './pages/Extensions';
import Models from './pages/Models';
import Approvals from './pages/Approvals';
import ErrorBoundary from './components/common/ErrorBoundary';
import Toast from './components/common/Toast';
import { AppProvider } from './contexts/AppContext';
import { PipelineProvider } from './contexts/PipelineContext';

function App() {
    return (
        <ErrorBoundary>
            <AppProvider>
                <PipelineProvider>
                    <Layout>
                        <Routes>
                            <Route path="/" element={<Landing />} />
                            <Route path="/models" element={<Models />} />
                            <Route path="/connectors" element={<Connectors />} />
                            <Route path="/extensions" element={<Extensions />} />
                            <Route path="/approvals" element={<Approvals />} />
                        </Routes>
                    </Layout>
                    <Toast />
                </PipelineProvider>
            </AppProvider>
        </ErrorBoundary>
    );
}

export default App;
