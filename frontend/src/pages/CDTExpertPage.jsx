// frontend/src/pages/CDTExpertPage.jsx

import React, { useState } from 'react';
import axios from 'axios';
import { FileCheck2, UploadCloud, LoaderCircle, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

const CDTExpertPage = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState('');

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

  const handleFileChange = (e) => {
    setAnalysisResult(null);
    setError('');
    setFile(e.target.files[0]);
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
    return (
      <ul className="space-y-3">
        {items.map((item, index) => (
          <li key={index} className="flex items-start p-3 bg-slate-100 dark:bg-slate-700/50 rounded-lg">
            {item.compliant ? (
              <CheckCircle className="flex-shrink-0 w-5 h-5 text-green-500 mr-3 mt-1" />
            ) : (
              <XCircle className="flex-shrink-0 w-5 h-5 text-red-500 mr-3 mt-1" />
            )}
            <div>
              <p className="font-semibold text-slate-800 dark:text-slate-200">{item.item}</p>
              <p className="text-sm text-slate-600 dark:text-slate-400">{item.justification}</p>
            </div>
          </li>
        ))}
      </ul>
    );
  };

  return (
    <div className="space-y-8">
      <div className="bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700">
        <div className="flex items-center text-blue-500 dark:text-blue-400 mb-4">
          <FileCheck2 size={32} className="mr-3" />
          <h2 className="text-2xl font-bold">CDT Expert: Validação de Dossiê Técnico</h2>
        </div>
        <p className="text-slate-600 dark:text-slate-400 mb-6">
          Envie um Dossiê Técnico em formato PDF. A IA fará uma análise de conformidade, comparando o documento com os principais requisitos da ANVISA, e gerará um checklist de validação.
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
          <button type="submit" disabled={loading || !file} className="w-full flex justify-center items-center bg-blue-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-blue-700 transition duration-300 disabled:bg-blue-300 dark:disabled:bg-slate-600">
            {loading ? <><LoaderCircle className="animate-spin mr-2" /> Analisando Dossiê...</> : 'Iniciar Análise de Conformidade'}
          </button>
        </form>

        {error && (
          <div className="mt-6 p-4 rounded-lg flex items-center text-sm bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-300">
            <AlertTriangle className="mr-3" /> {error}
          </div>
        )}
      </div>
      
      {analysisResult && (
        <div className="bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700 animate-fade-in">
          <h3 className="text-xl font-bold mb-2 text-slate-800 dark:text-slate-200">Relatório de Análise de Conformidade</h3>
          <p className="mb-6 text-slate-600 dark:text-slate-400">
            Análise para o produto: <span className="font-semibold">{analysisResult.product_type}</span>
          </p>
          
          {Object.keys(analysisResult.modules).map(moduleKey => (
            <div key={moduleKey} className="mb-6">
              <h4 className="text-lg font-semibold border-b border-slate-200 dark:border-slate-700 pb-2 mb-4 text-blue-600 dark:text-blue-400">
                {moduleKey}: {analysisResult.modules[moduleKey].title}
              </h4>
              {renderChecklist(analysisResult.modules[moduleKey].checklist)}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CDTExpertPage;