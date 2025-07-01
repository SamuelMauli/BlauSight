import React, { useState } from 'react';
import axios from 'axios';
import { BrainCircuit, LoaderCircle, AlertTriangle, FileText, CheckCircle, Search, Wrench, ShieldAlert } from 'lucide-react';

const AnalyzePage = () => {
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

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
      setError(err.response?.data?.error || 'Erro ao conectar ao servidor.');
    } finally {
      setLoading(false);
    }
  };

  const InfoBlock = ({ icon, title, children }) => (
    <div className="bg-slate-100 dark:bg-slate-700/50 p-4 rounded-lg">
      <div className="flex items-center mb-2">
        {icon}
        <h4 className="font-semibold ml-2">{title}</h4>
      </div>
      <div className="text-sm text-text-secondary-light dark:text-text-secondary-dark pl-8 space-y-2">
        {children}
      </div>
    </div>
  );

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="blausight-card">
        <div className="blausight-card-header">
          <div className="blausight-card-icon">
            <BrainCircuit size={22} />
          </div>
          <h2 className="blausight-card-title">Análise Preditiva e Solução Proposta</h2>
        </div>
        <p className="blausight-card-description">
          Descreva um novo desvio. A IA irá analisar, contextualizar com dados históricos, diagnosticar a causa raiz e propor um plano de ação.
        </p>
        <form onSubmit={handlePredict}>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Ex: Durante a compressão do lote CAP-9981, o sistema de exaustão de pós da sala S-05 falhou..."
            className="w-full p-4 border border-border-light dark:border-border-dark rounded-lg bg-bg-primary-light dark:bg-bg-primary-dark focus:ring-2 focus:ring-accent-primary focus:outline-none transition"
            rows="5"
            disabled={loading}
          />
          <button type="submit" disabled={loading || !description} className="blausight-button-primary mt-4">
            {loading ? <><LoaderCircle className="animate-spin mr-2" /> Analisando...</> : 'Analisar e Propor Solução'}
          </button>
        </form>
      </div>

      {error && (
        <div className="p-4 rounded-lg flex items-center text-sm bg-red-100 dark:bg-red-900/50 text-danger animate-fade-in">
          <AlertTriangle className="mr-3" /> {error}
        </div>
      )}

      {result && (
        <div className="blausight-card animate-fade-in">
          <div className="blausight-card-header">
            <div className="blausight-card-icon">
              <FileText size={22} />
            </div>
            <h3 className="blausight-card-title">Relatório de Análise de Desvio</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className={`p-4 rounded-lg flex flex-col items-center justify-center text-center ${result.prediction === 'Procedente' ? 'bg-red-100 dark:bg-red-900/50' : 'bg-green-100 dark:bg-green-900/50'}`}>
              <p className="text-sm font-medium text-text-secondary-light dark:text-text-secondary-dark">Predição</p>
              <p className={`text-2xl font-bold ${result.prediction === 'Procedente' ? 'text-danger' : 'text-success'}`}>{result.prediction}</p>
            </div>
            <div className="p-4 rounded-lg flex flex-col items-center justify-center text-center bg-slate-100 dark:bg-slate-700/50">
              <p className="text-sm font-medium text-text-secondary-light dark:text-text-secondary-dark">Confiança</p>
              <p className="text-2xl font-bold text-accent-primary dark:text-blue-400">{Math.round(result.probability * 100)}%</p>
            </div>
          </div>
          
          <div className="space-y-6">
            <InfoBlock icon={<Search size={16} className="text-warning"/>} title="Análise de Causa Raiz">
              <div>
                <p className="font-semibold text-text-primary-light dark:text-text-primary-dark">Causa Provável:</p>
                <p>{result.root_cause_analysis.probable_cause}</p>
              </div>
              <div>
                <p className="font-semibold text-text-primary-light dark:text-text-primary-dark">Evidência Histórica:</p>
                <p className="italic">"{result.root_cause_analysis.evidence}"</p>
              </div>
            </InfoBlock>
            
            <InfoBlock icon={<Wrench size={16} className="text-accent-primary"/>} title="Plano de Ação Proposto">
               <div>
                <p className="font-semibold text-text-primary-light dark:text-text-primary-dark">Ações Imediatas:</p>
                <ul className="list-disc pl-5">
                    {result.proposed_solution.immediate_actions.map((action, index) => <li key={index}>{action}</li>)}
                </ul>
              </div>
               <div>
                <p className="font-semibold text-text-primary-light dark:text-text-primary-dark">Ações Corretivas:</p>
                 <ul className="list-disc pl-5">
                    {result.proposed_solution.corrective_actions.map((action, index) => <li key={index}>{action}</li>)}
                </ul>
              </div>
            </InfoBlock>
            
            <InfoBlock icon={<ShieldAlert size={16} className="text-danger"/>} title="Desvios Similares para Consulta">
                <div className="flex flex-wrap gap-2">
                    {result.similar_deviations.map((id, index) => (
                        <span key={index} className="px-3 py-1 text-xs font-bold rounded-full bg-slate-200 dark:bg-slate-600 text-text-secondary-light dark:text-text-secondary-dark">
                            {id}
                        </span>
                    ))}
                </div>
            </InfoBlock>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyzePage;