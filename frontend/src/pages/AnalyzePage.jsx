import React, { useState } from 'react';
import axios from 'axios';
import { BrainCircuit, LoaderCircle, AlertTriangle, Sparkles } from 'lucide-react';

const AnalyzePage = () => {
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!description.trim()) {
      setError('Por favor, insira a descrição do desvio para análise.');
      return;
    }
    setLoading(true);
    setResult(null);
    setError('');

    try {
      const response = await axios.post(`${API_URL}/predict`, {
        description: description,
      });
      setResult(response.data);
    } catch (err) {
      const errorMsg = err.response?.data?.error || 'Não foi possível conectar ao servidor de análise.';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="bg-white dark:bg-slate-800 p-8 rounded-2xl shadow-lg border border-slate-200 dark:border-slate-700">
        <div className="flex items-center text-purple-500 dark:text-purple-400 mb-4">
          <BrainCircuit size={32} className="mr-3" />
          <h2 className="text-2xl font-bold">Análise Preditiva de Desvio</h2>
        </div>
        <p className="text-slate-600 dark:text-slate-400 mb-6">
          Insira a descrição de um novo desvio. A IA irá analisar o texto e prever se o desvio é procedente ou improcedente, com base nos dados históricos.
        </p>
        
        <form onSubmit={handleAnalyze}>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full h-40 p-3 border-2 border-slate-200 dark:border-slate-700 rounded-lg mb-4 focus:ring-2 focus:ring-purple-500 dark:bg-slate-900 dark:text-slate-200"
            placeholder="Descreva detalhadamente o desvio ocorrido aqui..."
            disabled={loading}
          />
          <button 
            type="submit" 
            disabled={loading || !description} 
            className="w-full flex justify-center items-center bg-purple-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-purple-700 transition duration-300 disabled:bg-purple-300 dark:disabled:bg-slate-600"
          >
            {loading ? <><LoaderCircle className="animate-spin mr-2" /> Analisando...</> : 'Analisar Desvio'}
          </button>
        </form>

        {error && (
          <div className="mt-6 p-4 rounded-lg flex items-center text-sm bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-300">
            <AlertTriangle className="mr-3" />
            {error}
          </div>
        )}

        {result && (
          <div className="mt-6 p-6 rounded-lg bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700">
              <h3 className="text-lg font-bold text-slate-800 dark:text-slate-200 flex items-center mb-4">
                <Sparkles className="mr-3 text-purple-500" />
                Resultado da Análise
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-white dark:bg-slate-800 rounded-lg shadow">
                      <p className="text-sm text-slate-500 dark:text-slate-400">Previsão</p>
                      <p className={`text-xl font-bold ${result.prediction === 'Procedente' ? 'text-green-600 dark:text-green-400' : 'text-orange-600 dark:text-orange-400'}`}>
                        {result.prediction}
                      </p>
                  </div>
                  <div className="p-4 bg-white dark:bg-slate-800 rounded-lg shadow">
                      <p className="text-sm text-slate-500 dark:text-slate-400">Nível de Confiança</p>
                      <p className="text-xl font-bold text-slate-700 dark:text-slate-300">
                        {(result.probability * 100).toFixed(2)}%
                      </p>
                  </div>
              </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalyzePage;