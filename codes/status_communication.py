from idle_algorithm.cal import Qos_value_algorithm

class status_communication():

    def status_check(self,action_a,container_n,container_u,action_Qos_time,action_Qos_value):
        '''
        return: renter id
        '''
        # renter_id_tmp = 0
        judge = Qos_value_algorithm(action_a,container_n,container_u,action_Qos_time)
        if judge > action_Qos_value and container_n >= 1:
            judge_1 = Qos_value_algorithm(action_a,container_n-1,container_u,action_Qos_time)
            if judge_1 > action_Qos_value:
                print('can be rented, Qos is',judge_1)
                #if (judge_1 == 1.0):
                #    print('---------------------------', [action_a,container_n-1,container_u,action_Qos_time])
                # renter_id_tmp = container_n
                return container_n

            elif judge_1 < 0:
                print('cannot be rented, Qos is 0')
            else:print('cannot be rented, Qos is', judge_1)
        elif judge < 0:
            print('cannot satisfy, Qos is 0')
        else:print('cannot satisfy, Qos is', judge)

        return 0
        # return renter_id_tmp

    #def status_stop(self,monitor_status):
    #    monitor_status.value = 0
#status_manager = status_communication()
#id_tmp = status_manager.status_check(5,6,1.78,0.8,0.95)
#print(id_tmp)
