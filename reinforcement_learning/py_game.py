import gym
import sys

def run_gym_environment(argv):
    # el primer parametro es el nombre a ejecutar
    environment = gym.make("Qbert-v0")
    MAX_NUM_EPISODES = 10
    MAX_STEPS_PER_EPISODE = 500

    
    for episodes in range(MAX_NUM_EPISODES):
        environment.reset()
        for step in range(MAX_STEPS_PER_EPISODE):
            environment.render()
            action = environment.action_space.sample()
            next_step, reward, done, info = environment.step(action)
            obs = next_step

            if done == True:
                print("\n Episodio#{}, terminado en {} pasos.".format(episode, step+1))
                break
        # -- lo que devuelve --
        # next_step, el estado despues de la accion en el entorno -> object
        #reward -> float
        #done -> Boolean (si en el siguiente step se reseta porque se termino el juego)
        #info -> dictionary 
    environment.close()

if __name__ == "__main__":
    run_gym_environment(sys.argv)