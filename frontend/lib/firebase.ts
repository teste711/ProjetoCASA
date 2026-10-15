import { initializeApp, getApps } from 'firebase/app';
import { getAuth } from 'firebase/auth';

// Preencha em frontend/.env.local (Firebase Console > Configurações do projeto > Seus apps > Web)
const app = getApps()[0] ?? initializeApp({
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
});

export const auth = getAuth(app);

/* Uso nas telas (cadastro / login / esqueci-senha):
   import { createUserWithEmailAndPassword, sendEmailVerification, signInWithEmailAndPassword,
            sendPasswordResetEmail, signOut } from 'firebase/auth';

   cadastro:  const { user } = await createUserWithEmailAndPassword(auth, email, senha);
              await sendEmailVerification(user);          // RF02: e-mail de confirmação
   login:     await signInWithEmailAndPassword(auth, email, senha);
              const perfil = (await api.get('/me')).data;  // cria o perfil no 1º acesso
   esqueci:   await sendPasswordResetEmail(auth, email);
   sair:      await signOut(auth);
*/
