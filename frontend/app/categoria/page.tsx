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
  Search,
  Filter,
  Plus,
  Pencil,
  Trash2,
  LayoutGrid,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RefreshCw,
  FolderOpen,
  Volume2,
  Eye
} from 'lucide-react';
import Link from 'next/link';

export default function Categoria() {
  const [temDados, setTemDados] = useState(true);
  const [temNotificacoes, setTemNotificacoes] = useState(true);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState<any>(null);
  const [categoriaParaExcluir, setCategoriaParaExcluir] = useState<any>(null);
  
  // NOVO: Estado para abrir o modal de detalhes da categoria acessada
  const [categoriaAcessada, setCategoriaAcessada] = useState<any>(null);

  const [searchTerm, setSearchTerm] = useState('');
  const [newCategoryName, setNewCategoryName] = useState('');
  const [editCategoryName, setEditCategoryName] = useState('');

  const [feedback, setFeedback] = useState<{
    tipo: 'sucesso' | 'erro' | 'atencao' | null;
    titulo: string;
    mensagem: string;
  }>({ tipo: null, titulo: '', mensagem: '' });

  // Lista mockada de categorias com os botões internos de cada uma
  const [categoriasList, setCategoriasList] = useState([
    { 
      id: 1, 
      nome: 'Escola', 
      slug: 'escola',
      botoes: [
        { id: 101, rotulo: 'Ir ao Banheiro', audio: 'banheiro.mp3' },
        { id: 102, rotulo: 'Lanche / Fome', audio: 'lanche.mp3' },
        { id: 103, rotulo: 'Caderno / Material', audio: 'caderno.mp3' },
        { id: 104, rotulo: 'Ouvir Música', audio: 'musica.mp3' }
      ]
    },
    { 
      id: 2, 
      nome: 'Casa', 
      slug: 'casa',
      botoes: [
        { id: 201, rotulo: 'Beber Água', audio: 'agua.mp3' },
        { id: 202, rotulo: 'Assistir TV', audio: 'tv.mp3' },
        { id: 203, rotulo: 'Dormir', audio: 'dormir.mp3' }
      ]
    },
    { 
      id: 3, 
      nome: 'Objetos', 
      slug: 'objetos',
      botoes: [
        { id: 301, rotulo: 'Brinquedo', audio: 'brinquedo.mp3' },
        { id: 302, rotulo: 'Mochila', audio: 'mochila.mp3' }
      ]
    },
  ]);

  const handleAddCategory = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCategoryName.trim()) {
      setFeedback({
        tipo: 'erro',
        titulo: 'Nome Inválido',
        mensagem: 'Por favor, digite um nome válido para a categoria.'
      });
      return;
    }

    const newCat = {
      id: Date.now(),
      nome: newCategoryName,
      slug: newCategoryName.toLowerCase().replace(/\s+/g, '-'),
      botoes: []
    };

    setCategoriasList([...categoriasList, newCat]);
    setNewCategoryName('');
    setShowAddModal(false);
    setFeedback({
      tipo: 'sucesso',
      titulo: 'Categoria Criada',
      mensagem: `A categoria "${newCat.nome}" foi adicionada com sucesso!`
    });
  };

  const handleEditCategory = (e: React.FormEvent) => {
    e.preventDefault();
    if (!editCategoryName.trim() || !showEditModal) return;

    setCategoriasList(categoriasList.map(cat => 
      cat.id === showEditModal.id ? { ...cat, nome: editCategoryName } : cat
    ));
    setShowEditModal(null);
    setFeedback({
      tipo: 'sucesso',
      titulo: 'Categoria Atualizada',
      mensagem: 'O nome da categoria foi alterado com sucesso.'
    });
  };

  const handleConfirmarExclusao = () => {
    if (!categoriaParaExcluir) return;
    setCategoriasList(categoriasList.filter(cat => cat.id !== categoriaParaExcluir.id));
    setCategoriaParaExcluir(null);
    setFeedback({
      tipo: 'sucesso',
      titulo: 'Categoria Removida',
      mensagem: 'A categoria foi excluída da prancha de comunicação.'
    });
  };

  const categoriasFiltradas = categoriasList.filter(cat => 
    cat.nome.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-800 flex font-sans relative">
      
      {/* SIDEBAR LATERAL */}
      <aside className="w-64 bg-white border-r border-slate-100 p-6 flex flex-col justify-between min-h-screen shadow-sm shrink-0">
        <div className="flex flex-col gap-8">
          <div className="flex justify-center w-full px-2">
            <div className="relative w-24 h-24 flex items-center justify-center shrink-0">
              <Image src="/logo.png" alt="Logo C.A.S.A" width={96} height={96} className="object-contain" priority />
            </div>
          </div>

          <nav className="flex flex-col gap-2">
            <Link href="/dashboard" className="flex items-center gap-3 px-4 py-3 rounded-2xl text-slate-500 hover:bg-slate-50 hover:text-[#5F7DE3] font-medium text-sm transition-all cursor-pointer">
              <Home className="w-5 h-5" /> Início
            </Link>
            <Link href="/categoria" className="flex items-center gap-3 px-4 py-3 rounded-2xl bg-[#5F7DE3] text-white font-medium text-sm shadow-md shadow-[#5F7DE3]/25 transition-all cursor-pointer">
              <Grid className="w-5 h-5" /> Categorias
            </Link>
            <Link href="/desempenho" className="flex items-center gap-3 px-4 py-3 rounded-2xl text-slate-500 hover:bg-slate-50 hover:text-[#5F7DE3] font-medium text-sm transition-all cursor-pointer">
              <BarChart2 className="w-5 h-5" /> Desempenho
            </Link>
            <Link href="/historico" className="flex items-center gap-3 px-4 py-3 rounded-2xl text-slate-500 hover:bg-slate-50 hover:text-[#5F7DE3] font-medium text-sm transition-all cursor-pointer">
              <History className="w-5 h-5" /> Histórico
            </Link>
            <Link href="/configuracoes" className="flex items-center gap-3 px-4 py-3 rounded-2xl text-slate-500 hover:bg-slate-50 hover:text-[#5F7DE3] font-medium text-sm transition-all cursor-pointer">
              <Settings className="w-5 h-5" /> Configurações
            </Link>
          </nav>
        </div>

        <div className="flex flex-col gap-3 pt-6 border-t border-slate-100">
          <div className="flex items-center justify-between p-2 rounded-2xl bg-slate-50 border border-slate-100">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-[#5F7DE3] text-white flex items-center justify-center font-bold text-sm">Z</div>
              <span className="font-semibold text-sm text-slate-700">Zeus Alves</span>
            </div>
            <ChevronDown className="w-4 h-4 text-slate-400" />
          </div>
          <Link href="/" className="w-full">
            <button className="flex items-center justify-center gap-2 w-full py-2.5 rounded-xl bg-slate-500 hover:bg-slate-600 text-white text-xs font-semibold transition-all shadow-sm cursor-pointer">
              <LogOut className="w-4 h-4" /> Desconectar
            </button>
          </Link>
        </div>
      </aside>

      {/* CONTEÚDO PRINCIPAL */}
      <main className="flex-1 p-8 flex flex-col gap-6 max-w-6xl mx-auto relative">
        
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
              {temDados ? 'Com Categorias' : 'Sem Categorias'}
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
          style={{ background: 'linear-gradient(90deg, #F5AC46 0%, #6586F3 52%, #4D66B8 88%, #3B4E8D 100%)' }}
        >
          <h1 className="text-3xl font-extrabold drop-shadow-sm">Categorias</h1>
        </section>

        <p className="text-center text-slate-400 text-xs max-w-md mx-auto leading-relaxed font-medium">
          Crie, edite ou elimine categorias. Em cada uma, você pode personalizar o que será exibido nos botões.
        </p>

        {/* FILTROS E BUSCA */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-2">
          <div className="flex items-center gap-3 w-full sm:w-auto flex-1">
            <div className="relative">
              <select className="appearance-none bg-white border border-slate-200 rounded-2xl px-10 py-3 text-xs font-medium text-slate-500 pr-10 cursor-pointer focus:outline-none shadow-xs">
                <option value="">Filtrar por</option>
                <option value="recentes">Mais recentes</option>
                <option value="az">A-Z</option>
              </select>
              <Filter className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5 pointer-events-none" />
              <ChevronDown className="w-4 h-4 text-slate-400 absolute right-3.5 top-3.5 pointer-events-none" />
            </div>

            <div className="relative flex-1 max-w-md">
              <input 
                type="text" 
                placeholder="Busque por uma categoria...."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-white border border-slate-200 rounded-2xl pl-10 pr-4 py-3 text-xs text-slate-700 placeholder:text-slate-400 focus:outline-none shadow-xs"
              />
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5 pointer-events-none" />
            </div>
          </div>

          <button 
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-6 py-3 bg-[#2589F5] hover:bg-[#1d78dc] text-white text-xs font-semibold rounded-2xl transition-all shadow-md shadow-blue-500/20 cursor-pointer w-full sm:w-auto justify-center"
          >
            <Plus className="w-4 h-4" />
            Adicionar Categoria
          </button>
        </div>

        {/* LISTA DE CATEGORIAS */}
        {temDados && categoriasFiltradas.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-2">
            {categoriasFiltradas.map((cat) => (
              <div 
                key={cat.id} 
                className="bg-[#F3F4F8] border border-slate-200/80 rounded-3xl p-6 shadow-xs flex flex-col justify-between h-40 hover:border-[#5F7DE3]/50 transition-all"
              >
                <div className="flex justify-between items-center px-2">
                  <div className="flex items-center gap-2 font-bold text-slate-700 text-sm">
                    <span>{cat.nome}</span>
                    <button 
                      onClick={() => {
                        setShowEditModal(cat);
                        setEditCategoryName(cat.nome);
                      }}
                      className="text-slate-400 hover:text-[#5F7DE3] transition-colors cursor-pointer"
                    >
                      <Pencil className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  
                  <button 
                    onClick={() => setCategoriaParaExcluir(cat)}
                    className="w-8 h-8 rounded-full border border-rose-200 bg-white flex items-center justify-center text-rose-500 hover:bg-rose-50 transition-colors cursor-pointer shadow-xs"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <button 
                  onClick={() => setCategoriaAcessada(cat)}
                  className="w-full py-2.5 rounded-2xl bg-[#5F7DE3] hover:bg-[#4d6bd3] text-white text-xs font-semibold transition-all shadow-sm cursor-pointer flex items-center justify-center gap-2"
                >
                  <Eye className="w-4 h-4" />
                  Acessar Categoria
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white border border-dashed border-slate-200 rounded-3xl p-12 text-center flex flex-col items-center justify-center gap-3 my-4">
            <FolderOpen className="w-12 h-12 text-slate-300" />
            <h3 className="font-bold text-slate-700 text-base">Nenhuma Categoria Encontrada</h3>
            <p className="text-xs text-slate-400 max-w-sm">
              Não há categorias cadastradas no momento. Clique no botão acima para adicionar a primeira.
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
                      <span className="text-[10px] text-slate-400">ESP32 operando normalmente</span>
                    </div>
                  </div>
                  <span className="text-[10px] text-purple-500 font-medium">Agora</span>
                </div>
              </div>
            ) : (
              <div className="bg-white/60 border border-slate-200/60 p-6 rounded-2xl text-center flex flex-col items-center gap-2">
                <Bell className="w-8 h-8 text-slate-300" />
                <span className="text-xs text-slate-500 font-medium">Nenhuma notificação no momento.</span>
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

      {/* MODAL DE CONTEÚDO DA CATEGORIA ACESSADA */}
      {categoriaAcessada && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
          <div className="bg-white w-full max-w-xl rounded-3xl p-6 sm:p-8 shadow-2xl border border-slate-100 relative flex flex-col gap-6 max-h-[85vh] overflow-y-auto">
            
            <button 
              onClick={() => setCategoriaAcessada(null)}
              className="absolute top-6 right-6 text-slate-400 hover:text-slate-600 transition-colors p-1 cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-3 border-b border-slate-100 pb-4">
              <div className="w-12 h-12 rounded-2xl bg-[#5F7DE3]/10 text-[#5F7DE3] flex items-center justify-center shrink-0 font-bold text-lg">
                <LayoutGrid className="w-6 h-6" />
              </div>
              <div className="flex flex-col text-left">
                <h3 className="text-xl font-bold text-slate-800">
                  Categoria: <span className="text-[#5F7DE3]">{categoriaAcessada.nome}</span>
                </h3>
                <span className="text-xs text-slate-400">
                  Gerencie os botões e frases atribuídas a esta prancha.
                </span>
              </div>
            </div>

            {/* LISTA DOS BOTÕES DA CATEGORIA */}
            <div className="flex flex-col gap-3">
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Botões Cadastrados ({categoriaAcessada.botoes?.length || 0})
              </h4>

              {categoriaAcessada.botoes && categoriaAcessada.botoes.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {categoriaAcessada.botoes.map((botao: any) => (
                    <div 
                      key={botao.id}
                      className="bg-slate-50 border border-slate-100 p-4 rounded-2xl flex items-center justify-between"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-xl bg-amber-500/10 text-amber-600 flex items-center justify-center font-bold text-xs">
                          <Volume2 className="w-4 h-4" />
                        </div>
                        <div className="flex flex-col text-left">
                          <span className="text-xs font-bold text-slate-800">{botao.rotulo}</span>
                          <span className="text-[10px] text-slate-400">{botao.audio}</span>
                        </div>
                      </div>

                      <button 
                        onClick={() => {
                          setFeedback({
                            tipo: 'sucesso',
                            titulo: 'Áudio Testado',
                            mensagem: `Simulando reprodução de voz: "${botao.rotulo}"`
                          });
                        }}
                        className="p-1.5 text-[#5F7DE3] hover:bg-[#5F7DE3]/10 rounded-lg transition-colors cursor-pointer"
                        title="Ouvir Áudio"
                      >
                        <Volume2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-slate-50 border border-dashed border-slate-200 rounded-2xl p-6 text-center">
                  <span className="text-xs text-slate-400 font-medium">Nenhum botão cadastrado nesta categoria.</span>
                </div>
              )}
            </div>

            <div className="flex items-center gap-3 pt-2">
              <button 
                onClick={() => {
                  setFeedback({
                    tipo: 'sucesso',
                    titulo: 'Novo Botão',
                    mensagem: 'Prancha atualizada com o novo botão!'
                  });
                }}
                className="flex-1 py-3 rounded-2xl bg-[#5F7DE3] hover:bg-[#4d6bd3] text-white font-semibold text-xs transition-all shadow-md cursor-pointer flex items-center justify-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Adicionar Novo Botão
              </button>

              <button 
                onClick={() => setCategoriaAcessada(null)}
                className="px-6 py-3 rounded-2xl bg-slate-100 text-slate-600 font-semibold text-xs transition-all cursor-pointer"
              >
                Fechar
              </button>
            </div>

          </div>
        </div>
      )}

      {/* MODAL ADICIONAR CATEGORIA */}
      {showAddModal && (
        <div className="fixed inset-0 bg-slate-900/30 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
          <div className="bg-[#F3EFF5] w-full max-w-md rounded-3xl p-8 shadow-2xl border border-indigo-100 relative flex flex-col items-center text-center">
            <button onClick={() => setShowAddModal(false)} className="absolute top-6 right-6 text-slate-400 hover:text-slate-600 p-1 cursor-pointer">
              <X className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-2 mb-2">
              <LayoutGrid className="w-6 h-6 text-[#5F7DE3]" />
              <h3 className="text-xl font-bold text-[#5F7DE3]">Adicionar <span className="text-amber-500">Categoria</span></h3>
            </div>
            <p className="text-xs text-slate-500 max-w-xs mb-6 font-medium">Informe o nome para criar a nova categoria.</p>
            <form onSubmit={handleAddCategory} className="w-full flex flex-col gap-4">
              <input 
                type="text" 
                placeholder="Exemplo: Rotina Matinal..."
                value={newCategoryName}
                onChange={(e) => setNewCategoryName(e.target.value)}
                className="w-full bg-white/90 border border-purple-200/80 rounded-2xl px-4 py-3 text-xs text-slate-700 placeholder:text-slate-400 focus:outline-none focus:border-[#5F7DE3] shadow-xs"
                autoFocus
              />
              <button type="submit" className="w-full py-3.5 rounded-2xl bg-[#5F7DE3] hover:bg-[#4d6bd3] text-white font-semibold text-sm transition-all shadow-md shadow-[#5F7DE3]/25 cursor-pointer">
                Salvar Categoria
              </button>
            </form>
          </div>
        </div>
      )}

      {/* MODAL EDITAR CATEGORIA */}
      {showEditModal && (
        <div className="fixed inset-0 bg-slate-900/30 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
          <div className="bg-[#F3EFF5] w-full max-w-md rounded-3xl p-8 shadow-2xl border border-indigo-100 relative flex flex-col items-center text-center">
            <button onClick={() => setShowEditModal(null)} className="absolute top-6 right-6 text-slate-400 hover:text-slate-600 p-1 cursor-pointer">
              <X className="w-5 h-5" />
            </button>
            <h3 className="text-xl font-bold text-[#5F7DE3] mb-2">Editar Categoria</h3>
            <form onSubmit={handleEditCategory} className="w-full flex flex-col gap-4 mt-4">
              <input 
                type="text" 
                value={editCategoryName}
                onChange={(e) => setEditCategoryName(e.target.value)}
                className="w-full bg-white/90 border border-purple-200/80 rounded-2xl px-4 py-3 text-xs text-slate-700 focus:outline-none focus:border-[#5F7DE3] shadow-xs"
              />
              <button type="submit" className="w-full py-3.5 rounded-2xl bg-[#5F7DE3] hover:bg-[#4d6bd3] text-white font-semibold text-sm transition-all shadow-md cursor-pointer">
                Atualizar Nome
              </button>
            </form>
          </div>
        </div>
      )}

      {/* MODAL EXCLUSÃO */}
      {categoriaParaExcluir && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-200">
          <div className="bg-white w-full max-w-sm rounded-3xl p-6 shadow-2xl border border-slate-100 text-center flex flex-col items-center gap-4">
            <div className="w-14 h-14 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center">
              <AlertTriangle className="w-7 h-7" />
            </div>
            <div className="flex flex-col gap-1">
              <h3 className="text-lg font-bold text-slate-800">Deseja excluir?</h3>
              <p className="text-xs text-slate-500">Tem certeza que deseja apagar a categoria <strong>&quot;{categoriaParaExcluir.nome}&quot;</strong>?</p>
            </div>
            <div className="grid grid-cols-2 gap-3 w-full mt-2">
              <button onClick={() => setCategoriaParaExcluir(null)} className="py-3 rounded-2xl bg-slate-100 text-slate-600 font-semibold text-xs cursor-pointer">Cancelar</button>
              <button onClick={handleConfirmarExclusao} className="py-3 rounded-2xl bg-rose-600 text-white font-semibold text-xs shadow-md shadow-rose-600/20 cursor-pointer">Sim, Excluir</button>
            </div>
          </div>
        </div>
      )}

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
            <button onClick={() => setFeedback({ tipo: null, titulo: '', mensagem: '' })} className="w-full py-3 rounded-2xl bg-[#5F7DE3] text-white font-semibold text-xs cursor-pointer">OK</button>
          </div>
        </div>
      )}

    </div>
  );
}