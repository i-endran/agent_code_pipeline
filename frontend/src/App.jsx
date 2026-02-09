import { Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Landing from './pages/Landing'
import Connectors from './pages/Connectors'
import Extensions from './pages/Extensions'
import Models from './pages/Models'

function App() {
    return (
        <Layout>
            <Routes>
                <Route path="/" element={<Landing />} />
                <Route path="/connectors" element={<Connectors />} />
                <Route path="/extensions" element={<Extensions />} />
                <Route path="/models" element={<Models />} />
            </Routes>
        </Layout>
    )
}

export default App
