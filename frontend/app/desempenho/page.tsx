'use client';

import { useState } from 'react';
import Image from 'next/image';
import { 
  Home, 
  Grid, 
  BarChart2, 
  History, 
  Settings, 
  Bell, 
  LogOut,
  ChevronDown,
  X,
  Filter,
  Download,
  RefreshCw,
  PieChart,
  CheckCircle2,
  XCircle,
  AlertTriangle
} from 'lucide-react';
import Link from 'next/link';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';

export default function Desempenho() {
  const [temDados, setTemDados] = useState(true);
  const [temNotificacoes, setTemNotificacoes] = useState(true);
  const [showNotifications, setShowNotifications] = useState(false);

  const [feedback, setFeedback] = useState<{
    tipo: 'sucesso' | 'erro' | 'atencao' | null;
    titulo: string;
    mensagem: string;
  }>({ tipo: null, titulo: '', mensagem: '' });

  const data = [
    { name: '0', valor: 200 },
    { name: '2', valor: 350 },
    { name: '4', valor: 380 },
    { name: '6', valor: 420 },
    { name: '8', valor: 750 },
    { name: '10', valor: 500 },
    { name: '12', valor: 550 },
    { name: '14', valor: 320 },
  ];

  const handleGerarPDF = () => {
    setFeedback({
      tipo: 'sucesso',
      titulo: 'Relatório Gerado',
      mensagem: 'O relatório de desempenho em PDF foi gerado e o download começará em instantes.'
    });
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-800 flex font-sans relative">
      
      {/* SIDEBAR LATERAL */}
      <aside className="w-64 bg-white border-r border-slate-100 p-6 flex flex-col justify-between min-h-screen shadow-sm shrink-0">
        <div className="flex flex-col gap-8">
          
          <div className="flex justify-center w-full px-2">
            <div className="relative w-24 h-24 flex items-center justify-center shrink-0">
              <Image 
                src="/logo.png" 
                alt="Logo C.A.S.A" 
                width={96} 
                height={96} 
                className="object-contain"
                priority 
              />
            </div>
          </div>

          <nav className="flex flex-col gap-2">
            <Link 
              href="/dashboard"
              className="flex items-center gap-3 px-4 py-3 rounded-2xl text-slate-500 hover:bg-slate-50 hover:text-[#5F7DE3] font-medium text-sm transition-all cursor-pointer"
            >
              <Home className="w-5 h-5" />
              Início
            </Link>

            <Link 
              href="/categoria"
              className="flex items-center gap-3 px-4 py-3 rounded-2xl text-slate-500 hover:bg-slate-50 hover:text-[#5F7DE3] font-medium text-sm transition-all cursor-pointer"
            >
              <Grid className="w-5 h-5" />
              Categorias
            </Link>

            <Link 
              href="/desempenho"
              className="flex items-center gap-3 px-4 py-3 rounded-2xl bg-[#5F7DE3] text-white font-medium text-sm shadow-md shadow-[#5F7DE3]/25 transition-all cursor-pointer"
            >
              <BarChart2 className="w-5 h-5" />
              Desempenho
            </Link>

            <Link 
              href="/historico"
              className="flex items-center gap-3 px-4 py-3 rounded-2xl text-slate-500 hover:bg-slate-50 hover:text-[#5F7DE3] font-medium text-sm transition-all cursor-pointer"
            >
              <History className="w-5 h-5" />
              Histórico
            </Link>

            <Link 
              href="/configuracoes"
              className="flex items-center gap-3 px-4 py-3 rounded-2xl text-slate-500 hover:bg-slate-50 hover:text-[#5F7DE3] font-medium text-sm transition-all cursor-pointer"
            >
              <Settings className="w-5 h-5" />
              Configurações
            </Link>
          </nav>
        </div>

        <div className="flex flex-col gap-3 pt-6 border-t border-slate-100">
          <div className="flex items-center justify-between p-2 rounded-2xl bg-slate-50 border border-slate-100">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-[#5F7DE3] text-white flex items-center justify-center font-bold text-sm">
                Z
              </div>
              <span className="font-semibold text-sm text-slate-700">Zeus Alves</span>
            </div>
            <ChevronDown className="w-4 h-4 text-slate-400" />
          </div>

          <Link href="/" className="w-full">
            <button className="flex items-center justify-center gap-2 w-full py-2.5 rounded-xl bg-slate-500 hover:bg-slate-600 text-white text-xs font-semibold transition-all shadow-sm cursor-pointer">
              <LogOut className="w-4 h-4" />
              Desconectar
            </button>
          </Link>
        </div>
      </aside>

      {/* CONTEÚDO PRINCIPAL */}
      <main className="flex-1 p-8 flex flex-col gap-6 max-w-5xl mx-auto relative">
        
        {/* BARRA SUPERIOR DE SIMULAÇÃO */}
        <div className="flex justify-between items-center bg-white p-3.5 rounded-2xl border border-slate-100 shadow-xs">
          <div className="flex items-center gap-3 text-xs text-slate-500">
            <span className="font-bold text-slate-700 flex items-center gap-1">
              <RefreshCw className="w-3.5 h-3.5 text-[#5F7DE3]" /> Simular Estado:
            </span>
            <button 
              onClick={() => setTemDados(!temDados)}
              className={`px-3 py-1 rounded-lg text-[11px] font-semibold transition-all cursor-pointer ${
                temDados ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'
              }`}
            >
              {temDados ? 'Com Relatórios' : 'Sem Relatórios'}
            </button>
            <button 
              onClick={() => setTemNotificacoes(!temNotificacoes)}
              className={`px-3 py-1 rounded-lg text-[11px] font-semibold transition-all cursor-pointer ${
                temNotificacoes ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-500'
              }`}
            >
              {temNotificacoes ? 'Com Notificações' : 'Sem Notificações'}
            </button>
          </div>

          <button 
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2.5 rounded-2xl bg-slate-50 border border-slate-100 text-[#5F7DE3] hover:bg-slate-100 transition-all shadow-xs relative cursor-pointer"
          >
            <Bell className="w-5 h-5" />
            {temNotificacoes && (
              <span className="absolute top-2 right-2 w-2.5 h-2.5 rounded-full bg-amber-400 border-2 border-white"></span>
            )}
          </button>
        </div>

        <section 
          className="w-full h-28 rounded-3xl p-8 flex items-center justify-center text-white shadow-lg relative overflow-hidden text-center"
          style={{
            background: 'linear-gradient(90deg, #F5AC46 0%, #6586F3 52%, #4D66B8 88%, #3B4E8D 100%)'
          }}
        >
          <h1 className="text-3xl font-extrabold drop-shadow-sm">Desempenho</h1>
        </section>

        <p className="text-center text-slate-400 text-xs max-w-md mx-auto leading-relaxed font-medium">
          Desempenho Geral em relação aos botões mais e menos acionados pelo dispositivo.
        </p>

        {/* Filtro */}
        <div className="flex justify-start items-center mt-2">
          <div className="relative">
            <select className="appearance-none bg-white border border-slate-200 rounded-2xl px-10 py-3 text-xs font-medium text-slate-500 pr-10 cursor-pointer focus:outline-none shadow-xs">
              <option value="">Filtrar por</option>
              <option value="semana">Esta Semana</option>
              <option value="mes">Este Mês</option>
            </select>
            <Filter className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5 pointer-events-none" />
            <ChevronDown className="w-4 h-4 text-slate-400 absolute right-3.5 top-3.5 pointer-events-none" />
          </div>
        </div>

        {/* ÁREA DO GRÁFICO (COM DADOS / VAZIO) */}
        {temDados ? (
          <div className="w-full bg-white border border-slate-100 rounded-3xl p-6 shadow-xs flex flex-col gap-6 mt-2 relative">
            <div className="w-full h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
                  <XAxis 
                    dataKey="name" 
                    axisLine={{ stroke: '#F97316', strokeWidth: 3 }} 
                    tickLine={false} 
                    tick={{ fill: '#64748B', fontSize: 12, fontWeight: 600 }}
                  />
                  <YAxis 
                    axisLine={{ stroke: '#F97316', strokeWidth: 3 }} 
                    tickLine={false} 
                    tick={{ fill: '#64748B', fontSize: 12, fontWeight: 600 }}
                    domain={[0, 1000]}
                    ticks={[0, 200, 400, 600, 800, 1000]}
                  />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#FFF', borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.08)' }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="valor" 
                    stroke="#F97316" 
                    strokeWidth={4} 
                    dot={{ fill: '#F97316', r: 5, strokeWidth: 2, stroke: '#FFF' }}
                    activeDot={{ r: 7 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="flex justify-end w-full">
              <button 
                onClick={handleGerarPDF}
                className="flex items-center gap-2 px-6 py-3 bg-[#5F7DE3] hover:bg-[#4d6bd3] text-white text-xs font-semibold rounded-2xl transition-all shadow-md shadow-[#5F7DE3]/20 cursor-pointer"
              >
                <Download className="w-4 h-4" />
                Gerar PDF
              </button>
            </div>
          </div>
        ) : (
          <div className="bg-white border border-dashed border-slate-200 rounded-3xl p-12 text-center flex flex-col items-center justify-center gap-3 my-4">
            <PieChart className="w-12 h-12 text-slate-300" />
            <h3 className="font-bold text-slate-700 text-base">Sem Dados de Desempenho</h3>
            <p className="text-xs text-slate-400 max-w-sm">
              Inicie a utilização do dispositivo físico para gerar os primeiros gráficos de progresso e relatórios.
            </p>
          </div>
        )}

        {/* POP-UP DE NOTIFICAÇÕES */}
        {showNotifications && (
          <div className="absolute top-20 right-8 w-80 bg-[#F3EFF5] rounded-3xl p-6 shadow-2xl border border-indigo-100 z-50 animate-in fade-in zoom-in duration-200">
            <div className="flex justify-between items-center mb-6">
              <h4 className="text-lg font-bold text-[#5F7DE3]">Notificações</h4>
              <button 
                onClick={() => setShowNotifications(false)}
                className="text-slate-400 hover:text-slate-600 transition-colors p-1 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {temNotificacoes ? (
              <div className="flex flex-col gap-3">
                <div className="bg-white p-3.5 rounded-2xl shadow-xs flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-400 to-purple-400 shrink-0 flex items-center justify-center text-white text-xs font-bold">
                      ESP
                    </div>
                    <div className="flex flex-col">
                      <span className="text-xs font-semibold text-slate-800">Dispositivo Conectado</span>
                      <span className="text-[10px] text-slate-400">ESP32 sincronizado com sucesso</span>
                    </div>
                  </div>
                  <span className="text-[10px] text-purple-500 font-medium">Agora</span>
                </div>
              </div>
            ) : (
              <div className="bg-white/60 border border-slate-200/60 p-6 rounded-2xl text-center flex flex-col items-center gap-2">
                <Bell className="w-8 h-8 text-slate-300" />
                <span className="text-xs text-slate-500 font-medium">Nenhuma notificação por enquanto.</span>
              </div>
            )}

            <div className="text-center mt-6">
              <button 
                onClick={() => setShowNotifications(false)}
                className="text-xs text-slate-400 hover:text-slate-600 transition-colors cursor-pointer"
              >
                Fechar
              </button>
            </div>
          </div>
        )}

      </main>

      {/* MODAL FEEDBACK */}
      {feedback.tipo && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
          <div className="bg-white w-full max-w-sm rounded-3xl p-6 shadow-2xl border border-slate-100 text-center flex flex-col items-center gap-4">
            {feedback.tipo === 'sucesso' && <CheckCircle2 className="w-12 h-12 text-emerald-500" />}
            {feedback.tipo === 'erro' && <XCircle className="w-12 h-12 text-rose-500" />}
            {feedback.tipo === 'atencao' && <AlertTriangle className="w-12 h-12 text-amber-500" />}
            <div className="flex flex-col gap-1">
              <h3 className="text-lg font-bold text-slate-800">{feedback.titulo}</h3>
              <p className="text-xs text-slate-500">{feedback.mensagem}</p>
            </div>
            <button 
              onClick={() => setFeedback({ tipo: null, titulo: '', mensagem: '' })} 
              className="w-full py-3 rounded-2xl bg-[#5F7DE3] text-white font-semibold text-xs cursor-pointer"
            >
              OK
            </button>
          </div>
        </div>
      )}

    </div>
  );
}