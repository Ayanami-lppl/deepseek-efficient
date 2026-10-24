import csv, io, json, random, importlib.util, pathlib, sys
from decimal import Decimal
def load_module(p):
    spec=importlib.util.spec_from_file_location('candidate_'+p.parent.name,p)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def interval_cases():
    cases=[[],[(1,3),(3,5)],[(1,10),(2,4)],[(2,5),(1,3),(4,8)],[(0,0)],[(4,2)],[(-5,-1),(-3,2)],[(1,2),(1,2)],[(3,3),(1,4)],[(1,2),(2,2),(2,3)]]
    rng=random.Random(84136)
    for _ in range(200): cases.append([(rng.randint(-20,20),rng.randint(-20,20)) for _ in range(rng.randint(0,10))])
    for _ in range(100):
        xs=[]
        for _ in range(rng.randint(0,12)):
            a,b=sorted((rng.randint(-30,30),rng.randint(-30,30)));xs.append((a,b))
        cases.append(xs)
    return cases

def interval_oracle(xs):
    if any(a>b for a,b in xs): raise ValueError()
    out=[]
    for a,b in sorted((a,b) for a,b in xs if a<b):
        if out and a<out[-1][1]: out[-1]=(out[-1][0],max(out[-1][1],b))
        else: out.append((a,b))
    return out

def csv_cases():
    cases=[('customer,amount\n',{}),('\ufeffcustomer,amount\nAlice,0.1\nAlice,0.2\n',{'Alice':Decimal('0.3')}),('customer,amount\n"A,B",1.23\n"A,B",2.77\n',{'A,B':Decimal('4.00')}),('customer,amount\n  A  ,  2.50  \n\n  \nB,-1.00\nA,0.50\n',{'A':Decimal('3.00'),'B':Decimal('-1.00')}),('customer,amount\r\nA,1e-2\r\nB,2\r\n',{'A':Decimal('.01'),'B':Decimal('2')}),('',{}),('name,amount\nA,1\n',ValueError),('customer,price\nA,1\n',ValueError),('customer,amount\nA,1,2\n',ValueError),('customer,amount\nA\n',ValueError),('customer,amount\n  ,1\n',ValueError),('customer,amount\nA,\n',ValueError)]
    for invalid in ['nan','NaN','Infinity','-Infinity','sNaN','abc','1_2x']:
        cases.append(('customer,amount\nA,'+invalid+'\n',ValueError))
    rng=random.Random(7221)
    for _ in range(100):
        buf=io.StringIO(); writer=csv.writer(buf,lineterminator='\n');writer.writerow(['customer','amount']); wanted={}
        for _ in range(rng.randint(0,20)):
            name=rng.choice(['Alpha','B, Co','客戶 C','X']);value=Decimal(rng.randint(-10000,10000))/100
            writer.writerow([name,str(value)]);wanted[name]=wanted.get(name,Decimal(0))+value
        cases.append((buf.getvalue(),wanted))
    return cases

def grade(trial):
    file=pathlib.Path(trial['workdir'])/trial['file']; errors=[]; passed=0
    try: module=load_module(file)
    except Exception as e: return {'id':trial['id'],'task':trial['task'],'arm':trial['arm'],'passed':False,'load_error':str(e),'passed_cases':0}
    cases=interval_cases() if trial['task']=='intervals' else csv_cases()
    for i,case in enumerate(cases):
        try:
            if trial['task']=='intervals':
                xs=list(case); before=xs.copy()
                try: expected=interval_oracle(xs)
                except ValueError: expected=ValueError
                try: actual=module.merge_intervals(xs)
                except ValueError:
                    if expected is not ValueError: raise
                else:
                    assert expected is not ValueError,'missing ValueError'
                    assert actual==expected,(actual,expected)
                    assert isinstance(actual,list) and all(isinstance(x,tuple) for x in actual),'return type'
                assert xs==before,'mutated input'
            else:
                text,expected=case
                try: actual=module.aggregate(text)
                except ValueError:
                    if expected is not ValueError: raise
                else:
                    assert expected is not ValueError,'missing ValueError'
                    assert isinstance(actual,dict),'return type'
                    assert actual==expected,(actual,expected)
                    assert list(actual)==list(expected),'changed insertion order'
                    assert all(isinstance(x,Decimal) for x in actual.values()),'amount is not Decimal'
            passed+=1
        except Exception as e:
            if len(errors)<12: errors.append({'case':i,'type':type(e).__name__,'error':str(e)})
    return {'id':trial['id'],'task':trial['task'],'arm':trial['arm'],'rep':trial['rep'],'passed':passed==len(cases),'passed_cases':passed,'total_cases':len(cases),'failures':errors}


def main():
    import argparse
    parser=argparse.ArgumentParser(description="Offline verifier for the published synthetic benchmark; does not call a model.")
    parser.add_argument("task",choices=["csv","intervals"])
    parser.add_argument("file",type=pathlib.Path)
    args=parser.parse_args()
    file=args.file.resolve()
    if not file.is_file():
        parser.error("artifact file does not exist")
    result=grade({"id":"artifact","task":args.task,"arm":"local","rep":1,"workdir":str(file.parent),"file":file.name})
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
