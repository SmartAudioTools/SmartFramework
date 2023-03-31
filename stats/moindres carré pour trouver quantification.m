
X=-10:0;
a=2;
b=5;
Yideal=a*X+b;
sigma=0.3;
Y=Yideal+sigma*randn(size(Yideal));
Xh=[X;ones(1,numel(X))];
XhPinv=(Xh*Xh')^-1*Xh;
P=XhPinv*Y';
Yreconstruct=P'*Xh;
plot(X,Yideal,'b',X,Y,'g*',X,Yreconstruct,'r');
legend('Yideal','Y','Yreconstruct');
plot(XhPinv')

% filtre
constant=ones(numel(f),1);
f(end:-1:1)*constant==1 % erreur de position nulle
n=568; % n quelquonce , bout de rampe
rampe=(n-numel(f)+1:n)
f(end:-1:1)*rampe'==n %erreur de vitesse nulle
%
% approche design par contrainte

n=11
C=[ones(1,n);(0:n-1)]
C*f'=[1,0]'

% on cherche f qui verifie C*f'=[1,0]' et qui soit un passe bas
%W= 1:11 % penalization des haute frequences
%sum(W.*(FFT*f).^2)  sous contrainte C*f'=[1,0]'
