import React, { useState } from 'react';
import axios from 'axios';
import { BrainCircuit, LoaderCircle, AlertTriangle, FileText, Search, Wrench, ShieldAlert, Zap, X, BookOpen } from 'lucide-react';

const AnalyzePage = () => {
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [documentUrl, setDocumentUrl] = useState('');
  const [modalTitle, setModalTitle] = useState('');

  const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    setError('');
    try {
      const response = await axios.post(`${API_URL}/predict`, { description });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Não foi possível conectar ao servidor de análise.');
    } finally {
      setLoading(false);
    }
  };

  const handleViewDocument = (deviationId) => {
    const docUrl = `${API_URL}/document/${deviationId}`;
    setDocumentUrl(docUrl);
    setModalTitle(`Visualizando Documento do Desvio: ${deviationId}`);
    setIsModalOpen(true);
  };

  const InfoBlock = ({ icon, title, children }) => (
    <div className="bg-slate-100 dark:bg-slate-800/60 p-5 rounded-lg border border-slate-200 dark:border-slate-700">
      <div className="flex items-center mb-3">
        {icon}
        <h4 className="font-semibold text-text-primary-light dark:text-text-primary-dark ml-3">{title}</h4>
      </div>
      <div className="text-sm text-text-secondary-light dark:text-text-secondary-dark pl-9 space-y-3">
        {children}
      </div>
    </div>
  );
  
  const RiskLevel = ({ level = "Indefinido" }) => {
    const levelStyles = {
      'Crítico': 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300',
      'Maior': 'bg-orange-100 text-orange-800 dark:bg-orange-900/50 dark:text-orange-300',
      'Menor': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300',
    };
    const style = levelStyles[level] || 'bg-slate-200 dark:bg-slate-600';
    return <span className={`px-3 py-1 text-xs font-bold rounded-full ${style}`}>{level}</span>;
  };

  // --- MODAL DEFINITIVO COM IFRAME ---
  const DocumentModal = () => (
    <div 
      className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4 sm:p-6 md:p-8" 
      onClick={() => setIsModalOpen(false)}
    >
      <div 
        className="bg-white dark:bg-slate-900 rounded-lg shadow-2xl w-full max-w-6xl h-[95vh] flex flex-col animate-fade-in-up" 
        onClick={e => e.stopPropagation()}
      >
        <div className="flex justify-between items-center p-4 border-b border-slate-200 dark:border-slate-700 flex-shrink-0">
          <h3 className="font-bold text-lg text-slate-800 dark:text-slate-200 truncate pr-4">{modalTitle}</h3>
          <button 
            onClick={() => setIsModalOpen(false)} 
            className="p-2 rounded-full text-slate-500 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700"
            aria-label="Fechar modal"
          >
            <X size={24} />
          </button>
        </div>
        <div className="p-2 bg-slate-200 dark:bg-slate-800 flex-grow h-full">
          {documentUrl ? (
            <iframe
              src={documentUrl}
              title={modalTitle}
              className="w-full h-full border-0 rounded"
              sandbox="allow-scripts allow-same-origin"
            />
          ) : (
            <div className="flex items-center justify-center h-full"><LoaderCircle className="animate-spin text-blue-500" size={40} /></div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <>
      {isModalOpen && <DocumentModal />}
      <div className="space-y-8 animate-fade-in p-4 md:p-0">
        <div className="blausight-card">
          <div className="blausight-card-header">
          <div className="blausight-card-icon"><BrainCircuit size={22} /></div>
          <h2 className="blausight-card-title">Análise Preditiva de Desvios (CAPA Inteligente)</h2>
        </div>
        <p className="blausight-card-description">
          Descreva um novo desvio. A IA irá contextualizar com o histórico, avaliar o risco, diagnosticar a causa raiz e propor um plano de ação completo.
        </p>
        <form onSubmit={handlePredict}>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Ex: Durante a compressão do lote CAP-9981, foi observada uma falha intermitente no sistema de exaustão de pós da sala S-05, resultando em contaminação..."
            className="w-full p-4 border border-border-light dark:border-border-dark rounded-lg bg-bg-primary-light dark:bg-bg-primary-dark focus:ring-2 focus:ring-accent-primary focus:outline-none transition"
            rows="5"
            disabled={loading}
          />
          <button type="submit" disabled={loading || !description} className="blausight-button-primary w-full md:w-auto mt-4">
            {loading ? <><LoaderCircle className="animate-spin mr-2" /> Analisando Risco e Propondo Ações...</> : 'Analisar Desvio'}
          </button>
        </form>
        </div>

        {error && (
          <div className="p-4 rounded-lg flex items-center text-sm bg-red-100 dark:bg-red-900/50 text-danger animate-fade-in">
            <AlertTriangle className="mr-3 flex-shrink-0" /> {error}
          </div>
        )}

        {result && (
          <div className="blausight-card animate-fade-in">
            <div className="blausight-card-header">
              <div className="blausight-card-icon"><FileText size={22} /></div>
              <h3 className="blausight-card-title">Relatório de Análise e Plano de Ação (CAPA)</h3>
            </div>
            
            <div className="space-y-6">
              <InfoBlock icon={<Zap size={16} className="text-orange-500"/>} title="Avaliação de Risco">
                <div>
                  <p className="font-semibold text-text-primary-light dark:text-text-primary-dark mb-2">Nível de Risco Identificado:</p>
                  <RiskLevel level={result.risk_assessment?.level} />
                </div>
                <div>
                  <p className="font-semibold text-text-primary-light dark:text-text-primary-dark mt-3">Justificativa:</p>
                  <p>{result.risk_assessment?.justification}</p>
                </div>
              </InfoBlock>

              <InfoBlock icon={<Search size={16} className="text-blue-500"/>} title="Análise de Causa Raiz (RCA)">
                <div>
                  <p className="font-semibold text-text-primary-light dark:text-text-primary-dark">Causa Provável:</p>
                  <p>{result.root_cause_analysis?.probable_cause}</p>
                </div>
                <div>
                  <p className="font-semibold text-text-primary-light dark:text-text-primary-dark mt-3">Evidência e Raciocínio:</p>
                  <p className="italic">"{result.root_cause_analysis?.evidence}"</p>
                </div>
              </InfoBlock>
            
              <InfoBlock icon={<Wrench size={16} className="text-green-500"/>} title="Plano de Ação Corretiva e Preventiva">
                <div>
                  <p className="font-semibold text-text-primary-light dark:text-text-primary-dark">Ações de Contenção (Imediatas):</p>
                  <ul className="list-disc pl-5">
                      {result.proposed_solution_capa?.containment_actions?.map((action, index) => <li key={index}>{action}</li>)}
                  </ul>
                </div>
                <div className="mt-3">
                  <p className="font-semibold text-text-primary-light dark:text-text-primary-dark">Ações Corretivas (Eliminar a Causa):</p>
                  <ul className="list-disc pl-5">
                      {result.proposed_solution_capa?.corrective_actions?.map((action, index) => <li key={index}>{action}</li>)}
                  </ul>
                </div>
                <div className="mt-3">
                  <p className="font-semibold text-text-primary-light dark:text-text-primary-dark">Ações Preventivas (Evitar Recorrência):</p>
                  <ul className="list-disc pl-5">
                      {result.proposed_solution_capa?.preventive_actions?.map((action, index) => <li key={index}>{action}</li>)}
                  </ul>
                </div>
              </InfoBlock>
              
              <InfoBlock icon={<BookOpen size={16} className="text-indigo-500"/>} title="Desvios Históricos Similares para Consulta">
                  <div className="flex flex-wrap gap-2">
                      {result.similar_deviations_ids?.length > 0 ? (
                          result.similar_deviations_ids.map((id) => (
                              <button 
                                key={id} 
                                onClick={() => handleViewDocument(id)}
                                className="px-3 py-1 text-xs font-mono font-bold rounded-full bg-slate-200 dark:bg-slate-600 text-text-secondary-light dark:text-text-secondary-dark hover:bg-blue-500 hover:text-white transition-colors"
                              >
                                  {id}
                              </button>
                          ))
                      ) : (
                          <p>Nenhum desvio similar encontrado no histórico recente.</p>
                      )}
                  </div>
              </InfoBlock>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default AnalyzePage;