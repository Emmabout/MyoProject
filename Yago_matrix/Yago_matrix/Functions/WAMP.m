function WA=WAMP(X,thres)
N=length(X); WA=0; 
for k=1:N-1 
  if abs(X(k)-X(k+1)) >= thres
    WA=WA+1; 
  end
end
end

