import React, { useState } from 'react';
import axios from 'axios';
import { FileCheck2, UploadCloud, LoaderCircle, AlertTriangle, CheckCircle, XCircle, FileWarning, BadgeInfo, ShieldCheck, ShieldHalf, ShieldX } from 'lucide-react';

const CDTExpertPage = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState('');

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

  const handleFileChange = (e) => {
    setAnalysisResult(null);
    setError('');
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === "application/pdf") {
      setFile(selectedFile);
    } else {
      setFile(null);
      setError("Por favor, selecione um arquivo no formato PDF.");
    }
  };

  const handleAnalyzeDossier = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Por favor, selecione um arquivo de dossiê para análise.');
      return;
    }
    setLoading(true);
    setAnalysisResult(null);
    setError('');

    const formData = new FormData();
    formData.append('dossier_file', file);

    try {
      const response = await axios.post(`${API_URL}/analyze-dossier`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setAnalysisResult(response.data);
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Não foi possível conectar ao servidor de análise.';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const renderChecklist = (items) => {
    if (!items || items.length === 0) {
      return <p className="text-sm text-slate-500 dark:text-slate-400">Nenhum item de checklist foi retornado para este módulo.</p>;
    }
    return (
      <ul className="space-y-3">
        {items.map((item, index) => (
          <li key={index} className="flex items-start p-3 bg-slate-100 dark:bg-slate-700/50 rounded-lg border border-slate-200 dark:border-slate-700">
            {item.is_compliant ? (
              <CheckCircle className="flex-shrink-0 w-5 h-5 text-green-500 mr-3 mt-0.5" />
            ) : (
              <XCircle className="flex-shrink-0 w-5 h-5 text-red-500 mr-3 mt-0.5" />
            )}
            <div>
              <p className="font-semibold text-slate-800 dark:text-slate-200">{item.item}</p>
              <p className="text-sm text-slate-600 dark:text-slate-400 italic">"{item.justification}"</p>
            </div>
          </li>
        ))}
      </ul>
    );
  };

  const OverallStatusBadge = ({ status }) => {
    const statusConfig = {
      "Requer Atenção Crítica": { icon: <ShieldX size={20} />, style: "bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300" },
      "Aprovado com Ressalvas": { icon: <ShieldHalf size={20} />, style: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300" },
      "Conformidade Alta": { icon: <ShieldCheck size={20} />, style: "bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300" },
    };
    const config = statusConfig[status] || { icon: <BadgeInfo size={20} />, style: "bg-slate-200 dark:bg-slate-600" };
    
    return (
      <span className={`inline-flex items-center gap-2 px-4 py-2 text-sm font-bold rounded-full ${config.style}`}>
        {config.icon}
        {status || 'Indefinido'}
      </span>
    );
  };

  return (
    <div className="space-y-8 p-4 md:p-0">
      <div className="blausight-card">
        <div className="blausight-card-header">
          <div className="blausight-card-icon"><FileCheck2 size={22} /></div>
          <h2 className="blausight-card-title">CDT Expert: Validação de Dossiê Técnico</h2>
        </div>
        <p className="blausight-card-description">
          Envie um Dossiê Técnico em PDF. A IA fará uma análise de conformidade profunda, com validação cruzada entre módulos, e gerará um relatório de risco e um checklist de validação.
        </p>
        <form onSubmit={handleAnalyzeDossier}>
          <div className="border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-xl p-6 text-center mb-4 cursor-pointer hover:border-blue-500 dark:hover:border-blue-400 transition-colors">
            <input type="file" id="dossier-upload" onChange={handleFileChange} className="hidden" accept=".pdf" disabled={loading} />
            <label htmlFor="dossier-upload" className="cursor-pointer">
              <UploadCloud className="mx-auto h-12 w-12 text-slate-400" />
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
                {file ? `Arquivo selecionado: ${file.name}` : 'Arraste e solte ou clique para selecionar o dossiê'}
              </p>
            </label>
          </div>
          <button type="submit" disabled={loading || !file} className="blausight-button-primary w-full md:w-auto">
            {loading ? <><LoaderCircle className="animate-spin mr-2" /> Validando Dossiê...</> : 'Iniciar Validação Completa'}
          </button>
        </form>

        {error && (
          <div className="mt-6 p-4 rounded-lg flex items-center text-sm bg-red-100 dark:bg-red-900/50 text-danger">
            <AlertTriangle className="mr-3 flex-shrink-0" /> {error}
          </div>
        )}
      </div>
      
      {analysisResult && (
        <div className="blausight-card animate-fade-in">
          <h3 className="text-xl font-bold mb-4 text-slate-800 dark:text-slate-200">Relatório de Análise de Conformidade</h3>
          
          <div className="bg-slate-100 dark:bg-slate-800/60 p-6 rounded-lg mb-8 border border-slate-200 dark:border-slate-700">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <p className="text-sm text-slate-600 dark:text-slate-400">Tipo de Produto Identificado</p>
                <p className="font-bold text-lg text-slate-800 dark:text-slate-200">{analysisResult.overall_summary?.product_type_identified || 'Não identificado'}</p>
              </div>
              <div className="text-left md:text-right">
                <p className="text-sm text-slate-600 dark:text-slate-400 mb-2">Diagnóstico Geral</p>
                <OverallStatusBadge status={analysisResult.overall_summary?.overall_status} />
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
              <p className="font-semibold text-slate-700 dark:text-slate-300">Sumário de Pontos Críticos:</p>
              <p className="text-sm italic text-slate-600 dark:text-slate-400">"{analysisResult.overall_summary?.critical_findings || 'Nenhum ponto crítico destacado.'}"</p>
            </div>
          </div>
          
          {analysisResult.was_truncated && (
             <div className="my-6 p-4 rounded-lg flex items-center text-sm bg-yellow-100 dark:bg-yellow-900/50 text-yellow-800 dark:text-yellow-300">
              <FileWarning className="mr-3 flex-shrink-0" /> O arquivo enviado é muito grande e foi analisado parcialmente. A análise pode estar incompleta.
            </div>
          )}
          
          {analysisResult.modules_validation && Object.keys(analysisResult.modules_validation).map(moduleKey => (
            <div key={moduleKey} className="mb-6">
              <h4 className="text-lg font-semibold border-b border-slate-200 dark:border-slate-700 pb-2 mb-4 text-blue-600 dark:text-blue-400 capitalize">
                {moduleKey.replace('_', ' ')}
              </h4>
              {renderChecklist(analysisResult.modules_validation[moduleKey])}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CDTExpertPage;