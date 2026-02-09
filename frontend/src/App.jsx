import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Landing from './pages/Landing';
import Connectors from './pages/Connectors';
import Extensions from './pages/Extensions';
import Models from './pages/Models';
import Approvals from './pages/Approvals';

function App() {
    return (
        <Layout>
            <Routes>
                <Route path="/" element={<Landing />} />
                <Route path="/models" element={<Models />} />
                <Route path="/connectors" element={<Connectors />} />
                <Route path="/extensions" element={<Extensions />} />
                <Route path="/approvals" element={<Approvals />} />
            </Routes>
        </Layout>
    )
}

export default App
